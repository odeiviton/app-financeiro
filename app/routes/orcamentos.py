from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from app.models import Orcamento, Categoria, Transacao

bp = Blueprint('orcamentos', __name__, url_prefix='/orcamentos')


@bp.route('/')
def listar():
    mes = request.args.get('mes', type=int, default=date.today().month)
    ano = request.args.get('ano', type=int, default=date.today().year)
    categorias = Categoria.query.filter_by(tipo='despesa').order_by(Categoria.nome).all()

    orcamentos = {}
    for o in Orcamento.query.filter_by(mes=mes, ano=ano).all():
        orcamentos[o.categoria_id] = o.limite

    gastos = {}
    for c in categorias:
        total = db.session.query(db.func.sum(Transacao.valor)).filter(
            Transacao.tipo == 'despesa',
            Transacao.categoria_id == c.id,
            db.extract('month', Transacao.data) == mes,
            db.extract('year', Transacao.data) == ano,
        ).scalar() or 0
        gastos[c.id] = round(total, 2)

    return render_template(
        'orcamentos.html',
        categorias=categorias,
        orcamentos=orcamentos,
        gastos=gastos,
        mes=mes,
        ano=ano,
    )


@bp.route('/salvar', methods=['POST'])
def salvar():
    mes = int(request.form.get('mes', date.today().month))
    ano = int(request.form.get('ano', date.today().year))
    for key, value in request.form.items():
        if key.startswith('limite_'):
            cat_id = int(key.split('_')[1])
            limite = float(value) if value else 0
            orc = Orcamento.query.filter_by(
                mes=mes, ano=ano, categoria_id=cat_id
            ).first()
            if limite > 0:
                if orc:
                    orc.limite = limite
                else:
                    orc = Orcamento(mes=mes, ano=ano, limite=limite, categoria_id=cat_id)
                    db.session.add(orc)
            elif orc:
                db.session.delete(orc)
    db.session.commit()
    return redirect(url_for('orcamentos.listar', mes=mes, ano=ano))
