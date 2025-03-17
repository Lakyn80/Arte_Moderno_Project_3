from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user, login_user
from werkzeug.utils import secure_filename
from functools import wraps
import os
import csv
from io import StringIO
from flask import make_response
from app.models import Order
from sqlalchemy.orm import joinedload
from app.forms.admin_forms import AdminUpdateOrderStatusForm
from app.forms.admin_forms import AdminUpdateOrderStatusForm, AdminUpdateOrderNoteForm


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



@admin.route("/export_orders_csv")
@admin_required
def export_orders_csv():
    orders = Order.query.all()

    si = StringIO()
    writer = csv.writer(si)

    # Hlavička CSV
    writer.writerow([
        "Číslo faktury",
        "Jméno",
        "Příjmení",
        "E-mail",
        "Celková cena (Kč)",
        "Datum vytvoření",
        "Stav",
        "Doručovací adresa",
        "Fakturační adresa"
    ])

    for order in orders:
        user = order.user
        writer.writerow([
            order.invoice_number or "",
            user.first_name or "",
            user.last_name or "",
            user.email or "",
            f"{order.total_price:.2f}",
            order.created_at.strftime("%d.%m.%Y %H:%M"),
            order.status,
            order.address or "",
            order.billing_address or ""
        ])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=export_objednavek.csv"
    output.headers["Content-type"] = "text/csv; charset=utf-8"
    return output




@admin.route("/orders", methods=["GET"])
@admin_required
def admin_orders():
    user_email = request.args.get("email")
    date_from = request.args.get("from")
    date_to = request.args.get("to")
    search_term = request.args.get("search")  # NOVÉ hledací pole (faktura/jméno)

    orders = Order.query.options(
        joinedload(Order.user),
        joinedload(Order.items).joinedload(OrderItem.product)
    )

    if user_email:
        orders = orders.join(User).filter(User.email.ilike(f"%{user_email}%"))

    if search_term:
        orders = orders.join(User).filter(
            db.or_(
                Order.invoice_number.ilike(f"%{search_term}%"),
                User.first_name.ilike(f"%{search_term}%"),
                User.last_name.ilike(f"%{search_term}%")
            )
        )

    if date_from:
        orders = orders.filter(Order.created_at >= date_from)
    if date_to:
        orders = orders.filter(Order.created_at <= date_to)

    orders = orders.order_by(Order.created_at.desc()).all()
    return render_template("admin_orders.html", orders=orders)


# 📄 Detail objednávky

@admin.route("/order/<int:order_id>", methods=["GET", "POST"])
@admin_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)

    status_form = AdminUpdateOrderStatusForm()
    note_form = AdminUpdateOrderNoteForm()

    # Změna stavu objednávky
    if status_form.validate_on_submit() and 'status' in request.form:
        order.status = status_form.status.data
        db.session.commit()
        flash("Stav objednávky byl úspěšně změněn.", "success")
        return redirect(url_for("admin.order_detail", order_id=order.id))

    # Předvyplnění formulářů
    status_form.status.data = order.status
    note_form.note.data = order.note

    return render_template("admin_order_detail.html", order=order, status_form=status_form, note_form=note_form)



@admin.route("/order/<int:order_id>/update_status", methods=["POST"])
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get("status")
    order.status = new_status
    db.session.commit()
    flash("Stav objednávky byl aktualizován.", "success")
    return redirect(url_for("admin.order_detail", order_id=order.id))

@admin.route("/order/<int:order_id>/update_note", methods=["POST"])
@admin_required
def update_order_note(order_id):
    order = Order.query.get_or_404(order_id)
    form = AdminUpdateOrderNoteForm()

    if form.validate_on_submit():
        order.note = form.note.data
        db.session.commit()
        flash("Poznámka byla uložena.", "success")
    else:
        flash("Chyba při ukládání poznámky.", "danger")

    return redirect(url_for("admin.order_detail", order_id=order.id))

@admin.route("/user/<int:user_id>")
@admin_required
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    user_orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    return render_template("admin_user_detail.html", user=user, orders=user_orders)
