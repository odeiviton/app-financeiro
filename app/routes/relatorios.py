from datetime import date
from flask import Blueprint, render_template, request
from app import db
from app.models import Transacao, Categoria

bp = Blueprint('relatorios', __name__, url_prefix='/relatorios')


@bp.route('/')
def relatorios():
    ano = request.args.get('ano', type=int, default=date.today().year)

    categorias = Categoria.query.order_by(Categoria.tipo, Categoria.nome).all()

    dados_anuais = []
    for cat in categorias:
        total = db.session.query(db.func.sum(Transacao.valor)).filter(
            Transacao.categoria_id == cat.id,
            db.extract('year', Transacao.data) == ano,
        ).scalar() or 0
        if total > 0:
            dados_anuais.append({
                'categoria': cat.nome,
                'tipo': cat.tipo,
                'cor': cat.cor,
                'total': round(total, 2),
            })

    receita_total = sum(d['total'] for d in dados_anuais if d['tipo'] == 'receita')
    despesa_total = sum(d['total'] for d in dados_anuais if d['tipo'] == 'despesa')

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
        meses.append({
            'numero': m,
            'receita': round(receita, 2),
            'despesa': round(despesa, 2),
        })

    nome_meses = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro',
    ]

    return render_template(
        'relatorios.html',
        ano=ano,
        dados_anuais=dados_anuais,
        receita_total=round(receita_total, 2),
        despesa_total=round(despesa_total, 2),
        meses=meses,
        saldo=round(receita_total - despesa_total, 2),
        nome_meses=nome_meses,
    )
