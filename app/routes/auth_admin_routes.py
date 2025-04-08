# app/routes/auth_admin_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from app import db, bcrypt, mail
from app.models import User
from app.forms.admin_forms import (
    AdminLoginForm,
    AdminChangePasswordForm,
    AdminResetRequestForm,
    AdminResetPasswordForm
)

auth_admin = Blueprint("auth_admin", __name__, url_prefix="/admin")

@auth_admin.route("/login", methods=["GET", "POST"])
def admin_login():
    if current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for("admin.dashboard"))

    form = AdminLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.role == 'admin' and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Přihlášení jako administrátor bylo úspěšné.", "success")
            return redirect(url_for("admin.dashboard"))
        flash("Neplatné přihlašovací údaje nebo nejste administrátor.", "danger")
    return render_template("admin/admin_login.html", form=form)

@auth_admin.route("/logout")
@login_required
def admin_logout():
    logout_user()
    flash("Byl jste odhlášen z administrace.", "info")
    return redirect(url_for("auth_admin.admin_login"))

@auth_admin.route("/change_password", methods=["GET", "POST"])
@login_required
def admin_change_password():
    form = AdminChangePasswordForm()
    if form.validate_on_submit():
        if not bcrypt.check_password_hash(current_user.password, form.old_password.data):
            flash("❌ Staré heslo není správné.", "danger")
        else:
            current_user.password = bcrypt.generate_password_hash(form.new_password.data).decode("utf-8")
            db.session.commit()
            flash("✅ Heslo bylo úspěšně změněno.", "success")
            return redirect(url_for("admin.dashboard"))
    return render_template("admin/admin_change_password.html", form=form)

@auth_admin.route("/reset_password", methods=["GET", "POST"])
def admin_reset_request():
    form = AdminResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.role == 'admin':
            serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
            token = serializer.dumps(user.email, salt="admin-reset-salt")
            reset_url = url_for("auth_admin.admin_reset_token", token=token, _external=True)

            msg = Message("Obnova hesla (ArteModerno)", sender="noreply@artemoderno.cz", recipients=[user.email])
            msg.body = f"""
Dobrý den,

klikněte na tento odkaz pro reset hesla (platný 30 minut):
{reset_url}

Pokud jste o reset nežádali, ignorujte tento e-mail.
"""
            mail.send(msg)
            flash("Resetovací odkaz byl odeslán na e-mail.", "info")
            return redirect(url_for("auth_admin.admin_login"))
        flash("Uživatel s tímto e-mailem neexistuje nebo není administrátor.", "danger")
    return render_template("admin/admin_reset_request.html", form=form)

@auth_admin.route("/reset_password/<token>", methods=["GET", "POST"])
def admin_reset_token(token):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = serializer.loads(token, salt="admin-reset-salt", max_age=1800)
    except Exception:
        flash("Odkaz je neplatný nebo vypršel.", "danger")
        return redirect(url_for("auth_admin.admin_reset_request"))

    user = User.query.filter_by(email=email, role='admin').first()
    if not user:
        flash("Uživatel nebyl nalezen.", "danger")
        return redirect(url_for("auth_admin.admin_reset_request"))

    form = AdminResetPasswordForm()
    if form.validate_on_submit():
        user.password = bcrypt.generate_password_hash(form.new_password.data).decode("utf-8")
        db.session.commit()
        flash("Heslo bylo úspěšně změněno.", "success")
        return redirect(url_for("auth_admin.admin_login"))
    return render_template("admin/admin_reset_password.html", form=form)
