from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app import db
from app.models import Categoria

bp = Blueprint('categorias', __name__, url_prefix='/categorias')


@bp.route('/')
def listar():
    categorias = Categoria.query.order_by(Categoria.tipo, Categoria.nome).all()
    return render_template('categorias.html', categorias=categorias)


@bp.route('/api')
def api_listar():
    tipo = request.args.get('tipo', '')
    query = Categoria.query.order_by(Categoria.tipo, Categoria.nome)
    if tipo:
        query = query.filter(Categoria.tipo == tipo)
    return jsonify([c.to_dict() for c in query.all()])


@bp.route('/criar', methods=['POST'])
def criar():
    nome = request.form.get('nome')
    tipo = request.form.get('tipo')
    cor = request.form.get('cor', '#6366f1')
    if nome and tipo:
        cat = Categoria(nome=nome, tipo=tipo, cor=cor)
        db.session.add(cat)
        db.session.commit()
    return redirect(url_for('categorias.listar'))


@bp.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    cat = Categoria.query.get_or_404(id)
    db.session.delete(cat)
    db.session.commit()
    return redirect(url_for('categorias.listar'))
