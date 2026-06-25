from datetime import datetime, timezone, date
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.models import Transacao, ContaFixa, Categoria

bp = Blueprint('dashboard', __name__, url_prefix='/')


@bp.route('/')
@login_required
def dashboard():
    hoje = date.today()
    mes_atual = request.args.get('mes', type=int, default=hoje.month)
    ano_atual = request.args.get('ano', type=int, default=hoje.year)

    _auto_launch_fixas(mes_atual, ano_atual)

    receitas = db.session.query(db.func.sum(Transacao.valor)).filter(
        Transacao.tipo == 'receita',
        db.extract('month', Transacao.data) == mes_atual,
        db.extract('year', Transacao.data) == ano_atual,
    ).scalar() or 0

    despesas = db.session.query(db.func.sum(Transacao.valor)).filter(
        Transacao.tipo == 'despesa',
        db.extract('month', Transacao.data) == mes_atual,
        db.extract('year', Transacao.data) == ano_atual,
    ).scalar() or 0

    investimentos = db.session.query(db.func.sum(Transacao.valor)).filter(
        Transacao.tipo == 'investimento',
        db.extract('month', Transacao.data) == mes_atual,
        db.extract('year', Transacao.data) == ano_atual,
    ).scalar() or 0

    saldo = round(receitas - despesas, 2)

    ranking = db.session.query(
        Categoria.nome, Categoria.cor, db.func.sum(Transacao.valor).label('total')
    ).join(Transacao, Categoria.id == Transacao.categoria_id).filter(
        Transacao.tipo == 'despesa',
        db.extract('month', Transacao.data) == mes_atual,
        db.extract('year', Transacao.data) == ano_atual,
    ).group_by(Categoria.id).order_by(db.func.sum(Transacao.valor).desc()).limit(5).all()

    ultimas = Transacao.query.order_by(Transacao.data.desc()).limit(5).all()

    meses = []
    for i in range(5, -1, -1):
        m = mes_atual - i
        a = ano_atual
        while m < 1:
            m += 12
            a -= 1
        receita_mes = db.session.query(db.func.sum(Transacao.valor)).filter(
            Transacao.tipo == 'receita',
            db.extract('month', Transacao.data) == m,
            db.extract('year', Transacao.data) == a,
        ).scalar() or 0
        despesa_mes = db.session.query(db.func.sum(Transacao.valor)).filter(
            Transacao.tipo == 'despesa',
            db.extract('month', Transacao.data) == m,
            db.extract('year', Transacao.data) == a,
        ).scalar() or 0
        meses.append({
            'mes': m,
            'ano': a,
            'receitas': round(receita_mes, 2),
            'despesas': round(despesa_mes, 2),
        })

    return render_template(
        'dashboard.html',
        saldo=saldo,
        receitas=round(receitas, 2),
        despesas=round(despesas, 2),
        investimentos=round(investimentos, 2),
        ranking=ranking,
        ultimas=ultimas,
        meses=meses,
        mes_atual=mes_atual,
        ano_atual=ano_atual,
        nome_meses=['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'],
    )


@bp.route('/api/chart-data')
@login_required
def chart_data():
    ano = request.args.get('ano', type=int, default=date.today().year)
    meses = []
    for m in range(1, 13):
        receita = db.session.query(db.func.sum(Transacao.valor)).filter(
            Transacao.tipo == 'receita',
            db.extract('month', Transacao.data) == m,
            db.extract('year', Transacao.data) == ano,
        ).scalar() or 0
        despesa = db.session.query(db.func.sum(Transacao.valor)).filter(
            Transacao.tipo == 'despesa',
            db.extract('month', Transacao.data) == m,
            db.extract('year', Transacao.data) == ano,
        ).scalar() or 0
        investimento = db.session.query(db.func.sum(Transacao.valor)).filter(
            Transacao.tipo == 'investimento',
            db.extract('month', Transacao.data) == m,
            db.extract('year', Transacao.data) == ano,
        ).scalar() or 0
        meses.append({'receita': round(receita, 2), 'despesa': round(despesa, 2), 'investimento': round(investimento, 2)})

    cats = []
    for c in Categoria.query.filter_by(tipo='despesa').order_by(Categoria.nome).all():
        total = db.session.query(db.func.sum(Transacao.valor)).filter(
            Transacao.tipo == 'despesa',
            Transacao.categoria_id == c.id,
            db.extract('year', Transacao.data) == ano,
        ).scalar() or 0
        if total > 0:
            cats.append({'nome': c.nome, 'total': round(total, 2), 'cor': c.cor})

    return jsonify({'meses': meses, 'categorias': cats})


def _auto_launch_fixas(mes, ano):
    contas = ContaFixa.query.filter_by(ativo=True).all()
    for conta in contas:
        ja_lancada = Transacao.query.filter(
            Transacao.descricao == conta.descricao,
            db.extract('month', Transacao.data) == mes,
            db.extract('year', Transacao.data) == ano,
        ).first()
        if not ja_lancada:
            dia = min(conta.dia_vencimento, 28)
            transacao = Transacao(
                descricao=conta.descricao,
                valor=conta.valor,
                tipo='despesa',
                data=date(ano, mes, dia),
                categoria_id=conta.categoria_id,
            )
            db.session.add(transacao)
    db.session.commit()
