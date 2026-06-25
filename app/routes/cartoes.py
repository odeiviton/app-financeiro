from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from app.models import Cartao, Parcelamento

bp = Blueprint('cartoes', __name__, url_prefix='/cartoes')


@bp.route('/')
def listar():
    cartoes = Cartao.query.order_by(Cartao.nome).all()
    return render_template('cartoes.html', cartoes=cartoes)


@bp.route('/criar', methods=['POST'])
def criar():
    nome = request.form.get('nome')
    dia_fechamento = int(request.form.get('dia_fechamento', 1))
    dia_vencimento = int(request.form.get('dia_vencimento', 1))
    if nome:
        cartao = Cartao(nome=nome, dia_fechamento=dia_fechamento, dia_vencimento=dia_vencimento)
        db.session.add(cartao)
        db.session.commit()
    return redirect(url_for('cartoes.listar'))


@bp.route('/editar/<int:id>', methods=['POST'])
def editar(id):
    cartao = Cartao.query.get_or_404(id)
    cartao.nome = request.form.get('nome')
    cartao.dia_fechamento = int(request.form.get('dia_fechamento', 1))
    cartao.dia_vencimento = int(request.form.get('dia_vencimento', 1))
    db.session.commit()
    return redirect(url_for('cartoes.listar'))


@bp.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    cartao = Cartao.query.get_or_404(id)
    Parcelamento.query.filter_by(cartao_id=id).delete()
    db.session.delete(cartao)
    db.session.commit()
    return redirect(url_for('cartoes.listar'))
