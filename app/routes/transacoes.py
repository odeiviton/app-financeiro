from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required
from app import db
from app.models import Transacao, Categoria

bp = Blueprint('transacoes', __name__, url_prefix='/transacoes')


@bp.route('/')
@login_required
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
    investimentos = sum(t.valor for t in transacoes if t.tipo == 'investimento')

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
        total_investimentos=round(investimentos, 2),
        saldo=round(receitas - despesas - investimentos, 2),
    )


@bp.route('/nova')
@login_required
def nova():
    return render_template('nova_transacao.html', active_nav='transacoes')


@bp.route('/criar', methods=['POST'])
@login_required
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
    flash('Transação adicionada com sucesso!', 'success')

    redirect_to = request.form.get('redirect') or url_for('transacoes.listar', mes=data.month, ano=data.year)
    return redirect(redirect_to)


@bp.route('/csv')
@login_required
def csv():
    mes = request.args.get('mes', type=int, default=date.today().month)
    ano = request.args.get('ano', type=int, default=date.today().year)
    transacoes = Transacao.query.filter(
        db.extract('month', Transacao.data) == mes,
        db.extract('year', Transacao.data) == ano,
    ).order_by(Transacao.data.desc()).all()

    linhas = ['Data,Descrição,Categoria,Tipo,Valor']
    for t in transacoes:
        linhas.append(f'{t.data.strftime("%d/%m/%Y")},"{t.descricao or ""}",{t.categoria.nome},{t.tipo},{t.valor:.2f}'.replace('.', ','))

    return Response(
        '\n'.join(linhas),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=transacoes_{mes}_{ano}.csv'}
    )


@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    transacao = Transacao.query.get_or_404(id)
    if request.method == 'POST':
        transacao.descricao = request.form.get('descricao', '')
        transacao.valor = float(request.form.get('valor', 0))
        transacao.data = date.fromisoformat(request.form.get('data', str(date.today())))
        transacao.categoria_id = int(request.form.get('categoria_id'))
        db.session.commit()
        flash('Transação atualizada!', 'success')
        return redirect(url_for('transacoes.listar', mes=transacao.data.month, ano=transacao.data.year))
    categorias = Categoria.query.order_by(Categoria.tipo, Categoria.nome).all()
    return render_template('editar_transacao.html', t=transacao, categorias=categorias)


@bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
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
