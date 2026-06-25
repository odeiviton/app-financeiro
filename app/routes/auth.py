from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app import db
from app.models import User

bp = Blueprint('auth', __name__, url_prefix='/')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        user = User.query.filter_by(email=email).first()
        if user and user.check_senha(senha):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.dashboard'))
        flash('Email ou senha inválidos.', 'error')
    return render_template('login.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado.', 'error')
        else:
            user = User(nome=nome, email=email)
            user.set_senha(senha)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('dashboard.dashboard'))
    return render_template('register.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
