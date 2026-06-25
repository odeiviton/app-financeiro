from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from app.models import ContaFixa, Categoria, Transacao

bp = Blueprint('contas_fixas', __name__, url_prefix='/contas-fixas')


@bp.route('/')
def listar():
    contas = ContaFixa.query.order_by(ContaFixa.dia_vencimento).all()
    categorias = Categoria.query.filter_by(tipo='despesa').order_by(Categoria.nome).all()
    hoje = date.today()
    return render_template(
        'contas_fixas.html',
        contas=contas,
        categorias=categorias,
        hoje=hoje,
    )


@bp.route('/criar', methods=['POST'])
def criar():
    descricao = request.form.get('descricao')
    valor = float(request.form.get('valor', 0))
    dia_vencimento = int(request.form.get('dia_vencimento', 1))
    categoria_id = int(request.form.get('categoria_id'))
    conta = ContaFixa(
        descricao=descricao,
        valor=valor,
        dia_vencimento=dia_vencimento,
        categoria_id=categoria_id,
    )
    db.session.add(conta)
    db.session.commit()
    return redirect(url_for('contas_fixas.listar'))


@bp.route('/editar/<int:id>', methods=['POST'])
def editar(id):
    conta = ContaFixa.query.get_or_404(id)
    conta.descricao = request.form.get('descricao')
    conta.valor = float(request.form.get('valor', 0))
    conta.dia_vencimento = int(request.form.get('dia_vencimento', 1))
    conta.categoria_id = int(request.form.get('categoria_id'))
    db.session.commit()
    return redirect(url_for('contas_fixas.listar'))


@bp.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    conta = ContaFixa.query.get_or_404(id)
    db.session.delete(conta)
    db.session.commit()
    return redirect(url_for('contas_fixas.listar'))


@bp.route('/lancar-todas', methods=['POST'])
def lancar_todas():
    mes = int(request.form.get('mes', date.today().month))
    ano = int(request.form.get('ano', date.today().year))
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
    return redirect(url_for('transacoes.listar', mes=mes, ano=ano))
