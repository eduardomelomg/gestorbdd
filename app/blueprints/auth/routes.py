import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import select
from app.extensions import db
from app.models.usuario import Usuario
from app.blueprints.auth.forms import LoginForm, ProfileForm

from . import bp


def save_foto(form_foto):
    """Helper to save profile photo and return filename."""
    random_hex = os.urandom(8).hex()
    _, f_ext = os.path.splitext(form_foto.filename)
    picture_fn = random_hex + f_ext
    
    # Ensure directory exists
    profiles_path = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles')
    if not os.path.exists(profiles_path):
        os.makedirs(profiles_path)
        
    picture_path = os.path.join(profiles_path, picture_fn)
    form_foto.save(picture_path)
    return f"uploads/profiles/{picture_fn}"


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        usuario = db.session.execute(
            select(Usuario).where(Usuario.email == form.email.data.lower())
        ).scalar_one_or_none()
        if usuario and usuario.ativo and usuario.check_password(form.password.data):
            login_user(usuario, remember=form.remember_me.data)
            next_page = request.args.get("next")
            flash(f"Bem-vindo, {usuario.nome}!", "success")
            return redirect(next_page or url_for("main.dashboard"))
        flash("E-mail ou senha inválidos.", "danger")
    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("auth.login"))


@bp.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.nome = form.nome.data
        current_user.username = form.username.data
        current_user.email = form.email.data.lower()
        
        if form.foto.data:
            foto_file = save_foto(form.foto.data)
            current_user.foto_perfil = foto_file
            
        if form.password.data:
            current_user.set_password(form.password.data)
            
        db.session.add(current_user)
        db.session.commit()
        flash("Seu perfil foi atualizado!", "success")
        return redirect(url_for("auth.perfil"))
    elif request.method == "GET":
        form.nome.data = current_user.nome
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    return render_template("auth/perfil.html", title="Meu Perfil", form=form)
