from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user, login_user
from werkzeug.utils import secure_filename
from functools import wraps
import os

from app import db, bcrypt, mail
from app.models import Product, OrderItem, CartItem, User
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from app.forms.admin_forms import (
    AdminLoginForm,
    AdminChangePasswordForm,
    AdminResetRequestForm,
    AdminResetPasswordForm
)

admin = Blueprint("admin", __name__, url_prefix="/admin")

# 🔐 Dekorátor pro admin přístup
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or getattr(current_user, 'role', '') != 'admin':
            flash("Přístup pouze pro administrátory.", "danger")
            return redirect(url_for("views.login"))
        return f(*args, **kwargs)
    return decorated_function

# 📊 Admin dashboard
@admin.route("/dashboard")
@admin_required
def dashboard():
    products = Product.query.all()
    return render_template("admin_dashboard.html", products=products)

# ➕ Přidání produktu
@admin.route("/add_product", methods=["GET", "POST"])
@admin_required
def add_product():
    if request.method == "POST":
        name = request.form["name"]
        price = float(request.form["price"])
        description = request.form["description"]
        position_id = int(request.form["position_id"])
        stock = int(request.form["stock"])
        image_file = request.files.get("image")
        image_filename = None

        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            upload_path = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
            os.makedirs(upload_path, exist_ok=True)
            image_path = os.path.join(upload_path, filename)
            image_file.save(image_path)
            image_filename = filename

        new_product = Product(
            name=name,
            price=price,
            description=description,
            position_id=position_id,
            stock=stock,
            image_filename=image_filename,
            is_active=True
        )
        db.session.add(new_product)
        db.session.commit()
        flash("Produkt byl úspěšně přidán.", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("add_product.html", product=None)

# ✏️ Úprava produktu
@admin.route("/edit_product/<int:product_id>", methods=["GET", "POST"])
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == "POST":
        product.name = request.form["name"]
        product.price = float(request.form["price"])
        product.description = request.form["description"]
        product.position_id = int(request.form["position_id"])
        product.stock = int(request.form["stock"])

        image_file = request.files.get("image")
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            upload_path = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
            os.makedirs(upload_path, exist_ok=True)
            image_path = os.path.join(upload_path, filename)
            image_file.save(image_path)
            product.image_filename = filename

        db.session.commit()
        flash("Produkt byl úspěšně upraven.", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("add_product.html", product=product)

# 🟡 Deaktivace (soft delete)
@admin.route("/delete_product/<int:product_id>", methods=["POST"])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = False
    db.session.commit()
    flash("Produkt byl deaktivován.", "warning")
    return redirect(url_for("admin.dashboard"))

# 🔄 Reaktivace produktu
@admin.route("/reactivate_product/<int:product_id>", methods=["POST"])
@admin_required
def reactivate_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = True
    db.session.commit()
    flash("Produkt byl opět aktivován.", "success")
    return redirect(url_for("admin.dashboard"))

# ❌ Trvalé smazání produktu
@admin.route("/hard_delete_product/<int:product_id>", methods=["POST"])
@admin_required
def hard_delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    CartItem.query.filter_by(product_id=product.id).delete()
    OrderItem.query.filter_by(product_id=product.id).delete()
    db.session.delete(product)
    db.session.commit()
    flash("Produkt byl trvale smazán včetně všech vazeb.", "danger")
    return redirect(url_for("admin.dashboard"))

# 🔑 Přihlášení admina
@admin.route("/login", methods=["GET", "POST"])
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
        else:
            flash("Neplatné přihlašovací údaje nebo nejste administrátor.", "danger")
    return render_template("admin_login.html", form=form)

# 🔐 Změna hesla přihlášeným adminem
@admin.route("/change_password", methods=["GET", "POST"])
@admin_required
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
    return render_template("admin_change_password.html", form=form)

# 📧 Reset hesla – požadavek na e-mail
@admin.route("/reset_password", methods=["GET", "POST"])
def admin_reset_request():
    form = AdminResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.role == 'admin':
            serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
            token = serializer.dumps(user.email, salt="admin-reset-salt")
            reset_url = url_for("admin.admin_reset_token", token=token, _external=True)

            msg = Message("Obnovení hesla (ArteModerno)", sender="noreply@artemoderno.cz", recipients=[user.email])
            msg.body = f"""
Dobrý den,

pro obnovení hesla klikněte na následující odkaz (platný 30 minut):

{reset_url}

Pokud jste o reset nežádali, ignorujte tento e-mail.
"""
            mail.send(msg)
            flash("Resetovací odkaz byl odeslán na e-mail.", "info")
            return redirect(url_for("admin.admin_login"))
        else:
            flash("Uživatel s tímto e-mailem neexistuje nebo není administrátor.", "danger")
    return render_template("admin_reset_request.html", form=form)

# 🔓 Reset hesla – zadání nového hesla
@admin.route("/reset_password/<token>", methods=["GET", "POST"])
def admin_reset_token(token):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = serializer.loads(token, salt="admin-reset-salt", max_age=1800)
    except Exception:
        flash("Odkaz je neplatný nebo vypršel.", "danger")
        return redirect(url_for("admin.admin_reset_request"))

    user = User.query.filter_by(email=email, role='admin').first()
    if not user:
        flash("Uživatel nebyl nalezen.", "danger")
        return redirect(url_for("admin.admin_reset_request"))

    form = AdminResetPasswordForm()
    if form.validate_on_submit():
        user.password = bcrypt.generate_password_hash(form.new_password.data).decode("utf-8")
        db.session.commit()
        flash("Heslo bylo úspěšně změněno.", "success")
        return redirect(url_for("admin.admin_login"))

    return render_template("admin_reset_password.html", form=form)
