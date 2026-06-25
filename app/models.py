from datetime import datetime, timezone, date
from app import db


class Categoria(db.Model):
    __tablename__ = 'categorias'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    cor = db.Column(db.String(7), default='#6366f1')

    transacoes = db.relationship('Transacao', backref='categoria', lazy='dynamic')
    contas_fixas = db.relationship('ContaFixa', backref='categoria', lazy='dynamic')
    orcamentos = db.relationship('Orcamento', backref='categoria', lazy='dynamic')
    parcelamentos = db.relationship('Parcelamento', backref='categoria', lazy='dynamic')

    def __repr__(self):
        return f'<Categoria {self.nome}>'

    def to_dict(self):
        return {'id': self.id, 'nome': self.nome, 'tipo': self.tipo, 'cor': self.cor}


class Transacao(db.Model):
    __tablename__ = 'transacoes'

    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), default='')
    valor = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    data = db.Column(db.Date, nullable=False, default=date.today)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    parcela_numero = db.Column(db.Integer, nullable=True)
    total_parcelas = db.Column(db.Integer, nullable=True)
    parcelamento_id = db.Column(db.Integer, db.ForeignKey('parcelamentos.id'), nullable=True)
    created_at = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f'<Transacao {self.descricao} R${self.valor}>'

    @property
    def mes_ano(self):
        return self.data.month, self.data.year


class ContaFixa(db.Model):
    __tablename__ = 'contas_fixas'

    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    dia_vencimento = db.Column(db.Integer, nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    @property
    def total_anual(self):
        return self.valor * 12


class Orcamento(db.Model):
    __tablename__ = 'orcamentos'

    id = db.Column(db.Integer, primary_key=True)
    mes = db.Column(db.Integer, nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    limite = db.Column(db.Float, nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('mes', 'ano', 'categoria_id', name='uq_orcamento'),
    )


class Cartao(db.Model):
    __tablename__ = 'cartoes'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    dia_fechamento = db.Column(db.Integer, nullable=False)
    dia_vencimento = db.Column(db.Integer, nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    parcelamentos = db.relationship('Parcelamento', backref='cartao', lazy='dynamic')

    def __repr__(self):
        return f'<Cartao {self.nome}>'


class Parcelamento(db.Model):
    __tablename__ = 'parcelamentos'

    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    valor_total = db.Column(db.Float, nullable=False)
    n_parcelas = db.Column(db.Integer, nullable=False)
    cartao_id = db.Column(db.Integer, db.ForeignKey('cartoes.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    transacoes = db.relationship('Transacao', backref='parcelamento', lazy='dynamic')

    @property
    def valor_parcela(self):
        return round(self.valor_total / self.n_parcelas, 2)

    def gerar_transacoes(self):
        from app import db
        valor_parcela = self.valor_parcela
        for i in range(self.n_parcelas):
            mes = self.data_inicio.month + i
            ano = self.data_inicio.year
            while mes > 12:
                mes -= 12
                ano += 1
            try:
                dia = min(self.data_inicio.day, 28)
                data_parcela = date(ano, mes, dia)
            except ValueError:
                data_parcela = date(ano, mes, 28)
            transacao = Transacao(
                descricao=f'{self.descricao} ({i+1}/{self.n_parcelas})',
                valor=valor_parcela,
                tipo='despesa',
                data=data_parcela,
                categoria_id=self.categoria_id,
                parcela_numero=i + 1,
                total_parcelas=self.n_parcelas,
                parcelamento_id=self.id,
            )
            db.session.add(transacao)
        db.session.commit()
