from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app import db
from app.models import Transacao, Categoria

bp = Blueprint('transacoes', __name__, url_prefix='/transacoes')


@bp.route('/')
def listar():
    mes = request.args.get('mes', type=int, default=date.today().month)
    ano = request.args.get('ano', type=int, default=date.today().year)
    tipo = request.args.get('tipo', '')
    categoria_id = request.args.get('categoria_id', type=int)

    query = Transacao.query.filter(
        db.extract('month', Transacao.data) == mes,
        db.extract('year', Transacao.data) == ano,
    )
    if tipo:
        query = query.filter(Transacao.tipo == tipo)
    if categoria_id:
        query = query.filter(Transacao.categoria_id == categoria_id)

    transacoes = query.order_by(Transacao.data.desc(), Transacao.id.desc()).all()

    receitas = sum(t.valor for t in transacoes if t.tipo == 'receita')
    despesas = sum(t.valor for t in transacoes if t.tipo == 'despesa')

    categorias = Categoria.query.order_by(Categoria.tipo, Categoria.nome).all()

    return render_template(
        'transacoes.html',
        transacoes=transacoes,
        categorias=categorias,
        mes=mes,
        ano=ano,
        tipo=tipo,
        categoria_id=categoria_id,
        total_receitas=round(receitas, 2),
        total_despesas=round(despesas, 2),
        saldo=round(receitas - despesas, 2),
    )


@bp.route('/criar', methods=['POST'])
def criar():
    descricao = request.form.get('descricao', '')
    valor = float(request.form.get('valor', 0))
    tipo = request.form.get('tipo')
    data = date.fromisoformat(request.form.get('data', str(date.today())))
    categoria_id = int(request.form.get('categoria_id'))

    transacao = Transacao(
        descricao=descricao,
        valor=valor,
        tipo=tipo,
        data=data,
        categoria_id=categoria_id,
    )
    db.session.add(transacao)
    db.session.commit()

    return redirect(url_for('transacoes.listar', mes=data.month, ano=data.year))


@bp.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    transacao = Transacao.query.get_or_404(id)
    mes = transacao.data.month
    ano = transacao.data.year
    if transacao.parcelamento_id:
        parcelamento = transacao.parcelamento
        db.session.delete(transacao)
        if not Transacao.query.filter_by(parcelamento_id=parcelamento.id).first():
            db.session.delete(parcelamento)
    else:
        db.session.delete(transacao)
    db.session.commit()
    return redirect(url_for('transacoes.listar', mes=mes, ano=ano))
