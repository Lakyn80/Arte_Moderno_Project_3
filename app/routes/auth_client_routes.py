# app/routes/auth_client_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from app import db, bcrypt, mail
from app.models import User
from app.forms.forms import ClientResetRequestForm, ClientResetPasswordForm

auth_client = Blueprint("auth_client", __name__, url_prefix="")

@auth_client.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash("Jste již přihlášen/a.", "info")
        return redirect(url_for("views.home"))

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("Hesla se neshodují!", "error")
            return redirect(url_for("auth_client.register"))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("E-mail je již používán.", "error")
            return redirect(url_for("auth_client.register"))

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(username=username, email=email, password=hashed_password, role='user')

        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash("Registrace proběhla úspěšně.", "success")
        return redirect(url_for("views.home"))

    return render_template("client/register.html")

@auth_client.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("Jste již přihlášen/a.", "info")
        return redirect(url_for("views.home"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Přihlášení úspěšné!", "success")
            return redirect(url_for("views.home"))

        flash("Neplatné přihlašovací údaje!", "error")

    return render_template("client/login.html")

@auth_client.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Byl jste úspěšně odhlášen.", "info")
    return redirect(url_for("views.home"))

@auth_client.route("/reset_password", methods=["GET", "POST"])
def client_reset_request():
    form = ClientResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data, role='user').first()
        if user:
            serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
            token = serializer.dumps(user.email, salt="user-reset-salt")
            reset_url = url_for("auth_client.client_reset_token", token=token, _external=True)

            msg = Message("Obnova hesla – ArteModerno",
                          sender="noreply@artemoderno.cz",
                          recipients=[user.email])
            msg.body = f"""Dobrý den,

Pro změnu hesla klikněte na tento odkaz (platí 30 minut):
{reset_url}

Pokud jste žádost neodesílali, ignorujte tento e-mail.
"""
            mail.send(msg)
            flash("Odkaz na obnovu hesla byl odeslán na váš e-mail.", "info")
            return redirect(url_for("auth_client.login"))

        flash("Uživatel s tímto e-mailem nebyl nalezen.", "warning")
    return render_template("client/client_reset_request.html", form=form)

@auth_client.route("/reset_password/<token>", methods=["GET", "POST"])
def client_reset_token(token):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = serializer.loads(token, salt="user-reset-salt", max_age=1800)
    except Exception:
        flash("Odkaz je neplatný nebo vypršel.", "danger")
        return redirect(url_for("auth_client.client_reset_request"))

    user = User.query.filter_by(email=email, role='user').first()
    if not user:
        flash("Uživatel nebyl nalezen.", "danger")
        return redirect(url_for("auth_client.client_reset_request"))

    form = ClientResetPasswordForm()
    if form.validate_on_submit():
        user.password = bcrypt.generate_password_hash(form.new_password.data).decode("utf-8")
        db.session.commit()
        flash("Heslo bylo úspěšně změněno.", "success")
        return redirect(url_for("auth_client.login"))
    return render_template("client/client_reset_password.html", form=form)
