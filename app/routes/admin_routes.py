from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, make_response
from flask_login import login_required, current_user, login_user
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from functools import wraps
from datetime import datetime
import os, csv
from io import StringIO

from app import db, bcrypt, mail
from app.models import Product, Order, OrderItem, CartItem, User, DiscountCode
from app.forms.admin_forms import (
    AdminLoginForm,
    AdminChangePasswordForm,
    AdminResetRequestForm,
    AdminResetPasswordForm,
    AdminUpdateOrderStatusForm,
    AdminUpdateOrderNoteForm,
    AdminDiscountForm,
)

from sqlalchemy.orm import joinedload

admin = Blueprint("admin", __name__, url_prefix="/admin")


# 🔐 Admin přístup
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or getattr(current_user, 'role', '') != 'admin':
            flash("Přístup pouze pro administrátory.", "danger")
            return redirect(url_for("views.login"))
        return f(*args, **kwargs)
    return decorated


# 📊 Dashboard
@admin.route("/dashboard")
@admin_required
def dashboard():
    products = Product.query.all()
    return render_template("admin/admin_dashboard.html", products=products)


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
            upload_path = os.path.join(current_app.root_path, 'static', 'uploads')
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

    return render_template("admin/add_product.html", product=None)


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

        if request.form.get("delete_image") == "on" and product.image_filename:
            try:
                os.remove(os.path.join(current_app.root_path, 'static', 'uploads', product.image_filename))
            except FileNotFoundError:
                pass
            product.image_filename = None

        image_file = request.files.get("image")
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            upload_path = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_path, exist_ok=True)
            image_path = os.path.join(upload_path, filename)
            image_file.save(image_path)
            product.image_filename = filename

        db.session.commit()
        flash("Produkt byl úspěšně upraven.", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/add_product.html", product=product)


# 🟡 Deaktivace produktu
@admin.route("/delete_product/<int:product_id>", methods=["POST"])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = False
    db.session.commit()
    flash("Produkt byl deaktivován.", "warning")
    return redirect(url_for("admin.dashboard"))


# 🔄 Reaktivace
@admin.route("/reactivate_product/<int:product_id>", methods=["POST"])
@admin_required
def reactivate_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = True
    db.session.commit()
    flash("Produkt byl opět aktivován.", "success")
    return redirect(url_for("admin.dashboard"))


# ❌ Trvalé smazání
@admin.route("/hard_delete_product/<int:product_id>", methods=["POST"])
@admin_required
def hard_delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    CartItem.query.filter_by(product_id=product.id).delete()
    OrderItem.query.filter_by(product_id=product.id).delete()
    db.session.delete(product)
    db.session.commit()
    flash("Produkt byl trvale smazán.", "danger")
    return redirect(url_for("admin.dashboard"))


# 🔑 Admin login
@admin.route("/login", methods=["GET", "POST"])
def admin_login():
    if current_user.is_authenticated and current_user.role == "admin":
        return redirect(url_for("admin.dashboard"))

    form = AdminLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.role == "admin" and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Přihlášení úspěšné.", "success")
            return redirect(url_for("admin.dashboard"))
        flash("Neplatné přihlašovací údaje.", "danger")

    return render_template("admin/admin_login.html", form=form)


# 🔐 Změna hesla
@admin.route("/change_password", methods=["GET", "POST"])
@admin_required
def admin_change_password():
    form = AdminChangePasswordForm()
    if form.validate_on_submit():
        if not bcrypt.check_password_hash(current_user.password, form.old_password.data):
            flash("Staré heslo není správné.", "danger")
        else:
            current_user.password = bcrypt.generate_password_hash(form.new_password.data).decode("utf-8")
            db.session.commit()
            flash("Heslo změněno.", "success")
            return redirect(url_for("admin.dashboard"))
    return render_template("admin/admin_change_password.html", form=form)


# 📧 Reset hesla – požadavek
@admin.route("/reset_password", methods=["GET", "POST"])
def admin_reset_request():
    form = AdminResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.role == "admin":
            serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
            token = serializer.dumps(user.email, salt="admin-reset-salt")
            reset_url = url_for("admin.admin_reset_token", token=token, _external=True)

            msg = Message("Obnova hesla (ArteModerno)", sender="noreply@artemoderno.cz", recipients=[user.email])
            msg.body = f"Odkaz pro reset hesla:\n{reset_url}\nPlatnost: 30 minut"
            mail.send(msg)

            flash("Odkaz byl odeslán na e-mail.", "info")
            return redirect(url_for("admin.admin_login"))

        flash("Uživatel neexistuje nebo není admin.", "danger")

    return render_template("admin/admin_reset_request.html", form=form)


# 🔓 Reset hesla – nové heslo
@admin.route("/reset_password/<token>", methods=["GET", "POST"])
def admin_reset_token(token):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = serializer.loads(token, salt="admin-reset-salt", max_age=1800)
    except Exception:
        flash("Token je neplatný nebo vypršel.", "danger")
        return redirect(url_for("admin.admin_reset_request"))

    user = User.query.filter_by(email=email, role="admin").first()
    if not user:
        flash("Uživatel nenalezen.", "danger")
        return redirect(url_for("admin.admin_reset_request"))

    form = AdminResetPasswordForm()
    if form.validate_on_submit():
        user.password = bcrypt.generate_password_hash(form.new_password.data).decode("utf-8")
        db.session.commit()
        flash("Heslo bylo změněno.", "success")
        return redirect(url_for("admin.admin_login"))

    return render_template("admin/admin_reset_password.html", form=form)


# 📤 Export objednávek do CSV
@admin.route("/export_orders_csv")
@admin_required
def export_orders_csv():
    orders = Order.query.all()
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["Faktura", "Jméno", "Příjmení", "E-mail", "Cena", "Datum", "Stav", "Doručovací", "Fakturační"])
    for order in orders:
        writer.writerow([
            order.invoice_number or "",
            order.user.first_name or "",
            order.user.last_name or "",
            order.user.email or "",
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


# 📋 Seznam objednávek
@admin.route("/orders")
@admin_required
def admin_orders():
    user_email = request.args.get("email")
    date_from = request.args.get("from")
    date_to = request.args.get("to")
    search_term = request.args.get("search")

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
    return render_template("admin/admin_orders.html", orders=orders)


# 📄 Detail objednávky
@admin.route("/order/<int:order_id>", methods=["GET", "POST"])
@admin_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    status_form = AdminUpdateOrderStatusForm()
    note_form = AdminUpdateOrderNoteForm()

    if status_form.validate_on_submit() and 'status' in request.form:
        order.status = status_form.status.data
        db.session.commit()
        flash("Stav objednávky byl změněn.", "success")
        return redirect(url_for("admin.order_detail", order_id=order.id))

    status_form.status.data = order.status
    note_form.note.data = order.note

    return render_template("admin/admin_order_detail.html", order=order, status_form=status_form, note_form=note_form)


# 🟢 Změna stavu objednávky
@admin.route("/order/<int:order_id>/update_status", methods=["POST"])
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = request.form.get("status")
    db.session.commit()
    flash("Stav objednávky byl aktualizován.", "success")
    return redirect(url_for("admin.order_detail", order_id=order.id))


# 📝 Uložení poznámky
@admin.route("/order/<int:order_id>/update_note", methods=["POST"])
@admin_required
def update_order_note(order_id):
    order = Order.query.get_or_404(order_id)
    form = AdminUpdateOrderNoteForm()
    if form.validate_on_submit():
        order.note = form.note.data
        db.session.commit()
        flash("Poznámka uložena.", "success")
    else:
        flash("Chyba při ukládání poznámky.", "danger")
    return redirect(url_for("admin.order_detail", order_id=order.id))


# 👤 Detail zákazníka
@admin.route("/user/<int:user_id>")
@admin_required
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    return render_template("admin/admin_user_detail.html", user=user, orders=orders)


# 💸 Slevové kódy
@admin.route("/discounts", methods=["GET", "POST"])
@admin_required
def manage_discounts():
    form = AdminDiscountForm()
    if form.validate_on_submit():
        new_code = DiscountCode(
            code=form.code.data.strip(),
            discount_percent=form.discount_percent.data,
            expires_at=form.expires_at.data
        )
        db.session.add(new_code)
        db.session.commit()
        flash("Slevový kód přidán.", "success")
        return redirect(url_for("admin.manage_discounts"))

    discount_codes = DiscountCode.query.order_by(DiscountCode.created_at.desc()).all()
    return render_template("admin/admin_discounts.html", form=form, discount_codes=discount_codes)


# 🔁 Obnovení viditelnosti
@admin.route("/order/<int:order_id>/restore", methods=["POST"])
@admin_required
def restore_order_for_user(order_id):
    order = Order.query.get_or_404(order_id)
    order.visible_to_user = True
    db.session.commit()
    flash("Objednávka obnovena pro klienta.", "success")
    return redirect(url_for("admin.user_detail", user_id=order.user_id))


# ❌ Skrytí objednávky
@admin.route("/order/<int:order_id>/hide", methods=["POST"])
@admin_required
def hide_order_from_user(order_id):
    order = Order.query.get_or_404(order_id)
    order.visible_to_user = False
    db.session.commit()
    flash("Objednávka byla skryta z profilu klienta.", "info")
    return redirect(url_for("admin.user_detail", user_id=order.user_id))
