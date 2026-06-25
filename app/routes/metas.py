from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import MetaFinanceira

bp = Blueprint('metas', __name__, url_prefix='/metas')


@bp.route('/')
@login_required
def listar():
    metas = MetaFinanceira.query.order_by(MetaFinanceira.created_at.desc()).all()
    return render_template('metas.html', metas=metas)


@bp.route('/criar', methods=['POST'])
@login_required
def criar():
    nome = request.form.get('nome', '').strip()
    valor_alvo = float(request.form.get('valor_alvo', 0))
    cor = request.form.get('cor', '#7c3aed')
    if nome and valor_alvo > 0:
        meta = MetaFinanceira(nome=nome, valor_alvo=valor_alvo, cor=cor)
        db.session.add(meta)
        db.session.commit()
        flash('Meta criada com sucesso!', 'success')
    return redirect(url_for('metas.listar'))


@bp.route('/atualizar/<int:id>', methods=['POST'])
@login_required
def atualizar(id):
    meta = MetaFinanceira.query.get_or_404(id)
    action = request.form.get('action')
    if action == 'add':
        valor = float(request.form.get('valor', 0))
        meta.valor_atual += valor
        flash(f'R$ {valor:.2f} adicionado à meta!', 'success')
    elif action == 'update':
        meta.nome = request.form.get('nome', meta.nome)
        meta.valor_alvo = float(request.form.get('valor_alvo', meta.valor_alvo))
        meta.valor_atual = float(request.form.get('valor_atual', meta.valor_atual))
        meta.cor = request.form.get('cor', meta.cor)
        flash('Meta atualizada!', 'success')
    db.session.commit()
    return redirect(url_for('metas.listar'))


@bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
def excluir(id):
    meta = MetaFinanceira.query.get_or_404(id)
    db.session.delete(meta)
    db.session.commit()
    flash('Meta excluída.', 'info')
    return redirect(url_for('metas.listar'))
