from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from functools import wraps
import os

from app import db
from app.models import Product

admin = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or getattr(current_user, 'role', '') != 'admin':
            flash("Přístup pouze pro administrátory.", "danger")
            return redirect(url_for("views.login"))
        return f(*args, **kwargs)
    return decorated_function


@admin.route("/dashboard")
@admin_required
def dashboard():
    products = Product.query.all()
    return render_template("admin_dashboard.html", products=products)


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


@admin.route("/delete_product/<int:product_id>", methods=["POST"])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = False
    db.session.commit()
    flash("Produkt byl deaktivován (soft delete).", "warning")
    return redirect(url_for("admin.dashboard"))


@admin.route("/reactivate_product/<int:product_id>", methods=["POST"])
@admin_required
def reactivate_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = True
    db.session.commit()
    flash("Produkt byl opět aktivován.", "success")
    return redirect(url_for("admin.dashboard"))
