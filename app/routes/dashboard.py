from datetime import datetime, timezone, date
from flask import Blueprint, render_template
from app import db
from app.models import Transacao, ContaFixa

bp = Blueprint('dashboard', __name__, url_prefix='/')


@bp.route('/')
def dashboard():
    hoje = date.today()
    mes_atual = hoje.month
    ano_atual = hoje.year

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

    saldo = round(receitas - despesas, 2)

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
        ultimas=ultimas,
        meses=meses,
        mes_atual=mes_atual,
        ano_atual=ano_atual,
    )
