from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Parcelamento, Cartao, Categoria

bp = Blueprint('parcelamentos', __name__, url_prefix='/parcelamentos')


@bp.route('/')
@login_required
def listar():
    parcelamentos = Parcelamento.query.order_by(Parcelamento.data_inicio.desc()).all()
    cartoes = Cartao.query.order_by(Cartao.nome).all()
    categorias = Categoria.query.filter_by(tipo='despesa').order_by(Categoria.nome).all()
    return render_template(
        'parcelamentos.html',
        parcelamentos=parcelamentos,
        cartoes=cartoes,
        categorias=categorias,
    )


@bp.route('/criar', methods=['POST'])
@login_required
def criar():
    descricao = request.form.get('descricao')
    valor_total = float(request.form.get('valor_total', 0))
    n_parcelas = int(request.form.get('n_parcelas', 1))
    cartao_id = int(request.form.get('cartao_id'))
    categoria_id = int(request.form.get('categoria_id'))
    data_inicio = date.fromisoformat(
        request.form.get('data_inicio', str(date.today()))
    )

    parcelamento = Parcelamento(
        descricao=descricao,
        valor_total=valor_total,
        n_parcelas=n_parcelas,
        cartao_id=cartao_id,
        categoria_id=categoria_id,
        data_inicio=data_inicio,
    )
    db.session.add(parcelamento)
    db.session.flush()
    parcelamento.gerar_transacoes()
    flash('Parcelamento criado com sucesso!', 'success')

    return redirect(url_for('parcelamentos.listar'))


@bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
def excluir(id):
    parcelamento = Parcelamento.query.get_or_404(id)
    from app.models import Transacao
    Transacao.query.filter_by(parcelamento_id=id).delete()
    db.session.delete(parcelamento)
    db.session.commit()
    flash('Parcelamento excluído.', 'info')
    return redirect(url_for('parcelamentos.listar'))
