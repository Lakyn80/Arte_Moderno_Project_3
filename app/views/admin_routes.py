import os
from flask import current_app, Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from functools import wraps
from app.models import Product
from app import db
from flask_login import current_user, login_user, login_required
from app.models import User  # Import modelu User
from app import bcrypt       # Import bcrypt pro ověřování hesla
from app.models import CartItem
from app.models import OrderItem

admin = Blueprint("admin", __name__, url_prefix="/admin")


# Dekorátor pro zabezpečení admin panelu
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Musíte být přihlášen/a jako administrátor.", "error")
            return redirect(url_for("admin.login"))

        if current_user.role != 'admin':
            flash("Nemáte oprávnění přistupovat k admin panelu.", "error")
            return redirect(url_for("views.home"))

        return f(*args, **kwargs)
    return decorated_function


from flask_login import login_user

@admin.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated and current_user.role == "admin":
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        admin_user = User.query.filter_by(username=username, role='admin').first()

        if admin_user and bcrypt.check_password_hash(admin_user.password, password):
            login_user(admin_user)  # Flask-Login
            flash("Úspěšně přihlášen!", "success")
            return redirect(url_for("admin.dashboard"))
        else:
            flash("Neplatné přihlašovací údaje!", "error")

    return render_template("admin.html")




@admin.route("/logout")
@admin_required
def logout():
    session.pop("admin_logged_in", None)
    flash("Byl jste úspěšně odhlášen.", "info")
    return redirect(url_for("admin.login"))

@admin.route("/dashboard")
@admin_required
def dashboard():
    print(f"DEBUG: Přihlášený uživatel: {current_user.username}, Role: {current_user.role}")
    products = Product.query.all()
    return render_template("admin_dashboard.html", products=products)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@admin.route('/add_product', methods=['GET', 'POST'])
@admin_required
def add_product():
    if request.method == 'POST':
        position_id = request.form.get('position_id')
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        stock = request.form.get('stock')
        image = request.files.get('image')

        # Debugging - Výpis všech hodnot pro ověření
        print(f"DEBUG - Pozice ID: {position_id}")
        print(f"DEBUG - Název: {name}")
        print(f"DEBUG - Cena: {price}")
        print(f"DEBUG - Sklad: {stock}")
        print(f"DEBUG - Obrázek: {image.filename if image else 'Žádný obrázek'}")

        # Kontrola povinných polí
        if not (position_id and name and price and stock):
            flash('Všechna povinná pole (pozice ID, název, cena, sklad) musí být vyplněna.', 'error')
            return redirect(url_for('admin.add_product'))

        try:
            # Vytvoření nového produktu
            new_product = Product(
                position_id=int(position_id),
                name=name,
                description=description,
                price=float(price),
                stock=int(stock)
            )

            # Zpracování obrázku
            if image:
                image_filename = secure_filename(image.filename)
                image_path = os.path.join('app/static/uploads', image_filename)
                image.save(image_path)
                new_product.image_filename = image_filename

            # Uložení produktu do databáze
            db.session.add(new_product)
            db.session.commit()

            flash('Produkt byl úspěšně přidán.', 'success')
            return redirect(url_for('admin.dashboard'))

        except Exception as e:
            print(f"CHYBA PŘI UKLÁDÁNÍ PRODUKTU: {e}")
            db.session.rollback()
            flash('Chyba při nahrávání produktu.', 'error')
            return redirect(url_for('admin.add_product'))

    return render_template('add_product.html')



@admin.route("/edit_product/<int:product_id>", methods=["GET", "POST"])
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == "POST":
        product.position_id = request.form.get("position_id")
        product.name = request.form.get("name")
        product.price = request.form.get("price")
        product.description = request.form.get("description")

        # Kontrola, zda má být smazán existující obrázek
        if request.form.get("delete_image"):
            if product.image_filename:
                # Smazání souboru z diskového úložiště
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image_filename)
                if os.path.exists(image_path):
                    os.remove(image_path)
                product.image_filename = None  # Smazání odkazu na obrázek v databázi

        # Nahrání nového obrázku
        image = request.files.get("image")
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            product.image_filename = filename

        db.session.commit()
        flash("Produkt byl úspěšně aktualizován!", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("edit_product.html", product=product)


@admin.route("/delete_product/<int:product_id>", methods=["POST"])
@admin_required
def delete_product(product_id):
    """Soft deletion: Deaktivace produktu (produkt se nezobrazí v galerii)."""
    product = Product.query.get_or_404(product_id)
    product.is_active = False  # nastavíme produkt jako neaktivní
    try:
        db.session.commit()
        flash("Produkt byl úspěšně deaktivován.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Při deaktivaci produktu došlo k chybě.", "error")
        return redirect(url_for("admin.dashboard"))
    
    # Odstraníme případné položky v košíku, které odkazují na tento produkt
    cart_items = CartItem.query.filter_by(product_id=product.id).all()
    for item in cart_items:
        db.session.delete(item)
    db.session.commit()
    
    return redirect(url_for("admin.dashboard"))

@admin.route("/hard_delete_product/<int:product_id>", methods=["POST"])
@admin_required
def hard_delete_product(product_id):
    """Fyzické smazání produktu z databáze, povoleno pouze u produktů, které nejsou součástí objednávek."""
    product = Product.query.get_or_404(product_id)
    order_item_count = OrderItem.query.filter_by(product_id=product.id).count()
    if order_item_count > 0:
        flash("Produkt je součástí objednávek a nelze jej trvale smazat. Použijte deaktivaci.", "error")
        return redirect(url_for("admin.dashboard"))
    try:
        db.session.delete(product)
        db.session.commit()
        flash("Produkt byl trvale smazán.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Při trvalém smazání produktu došlo k chybě.", "error")
    return redirect(url_for("admin.dashboard"))



@admin.route("/reactivate_product/<int:product_id>", methods=["POST"])
@admin_required
def reactivate_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = True  # Nastavíme produkt jako aktivní
    try:
        db.session.commit()
        flash("Produkt byl úspěšně reaktivován.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Při reaktivaci produktu došlo k chybě.", "error")
    return redirect(url_for("admin.dashboard"))

