from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import Inquiry
from app import db, mail  # importujeme db a mail z __init__.py
from flask_mail import Message
from app import db, bcrypt
from app.models import User
from flask_login import login_user, current_user, logout_user, login_required
from app.models import Product
from app.models import Inquiry, User, Product, CartItem
from flask import session
from datetime import datetime

views = Blueprint("views", __name__)
cart = Blueprint("cart", __name__, url_prefix="/cart")

@views.route("/", methods=["GET"])
def home():
    return render_template("home.html")  # jen příklad

@views.route("/galerie")
def galerie():
    products = Product.query.filter(Product.is_active == True, Product.stock > 0).all()
    print("DEBUG: Produkty v galerii:")
    for product in products:
        print(f"ID: {product.id}, Název: {product.name}, Popis: {product.description}, Cena: {product.price}, Sklad: {product.stock}")

    return render_template("galerie.html", products=products)


@views.route('/kontakt', methods=['GET', 'POST'])
def kontakt():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject') or 'Bez předmětu'
        message = request.form.get('message')

        try:
            owner_msg = Message(subject=f"Nová zpráva od {name} - {subject}",
                                sender=email,
                                recipients=['artemodernoblaha@gmail.com'],
                                body=f"Od: {name} <{email}>\n\n{message}")
            mail.send(owner_msg)

            confirmation_msg = Message(subject="Děkujeme za vaši zprávu",
                                       sender='artemodernoblaha@gmail.com',
                                       recipients=[email],
                                       body=f"Dobrý den {name},\n\nDěkujeme za vaši zprávu. Odpovíme vám co nejdříve.\n\nVaše zpráva:\n{message}\n\nS pozdravem,\nArte Moderno")
            mail.send(confirmation_msg)

            flash('Zpráva byla úspěšně odeslána! Potvrzení bylo zasláno na váš e-mail.', 'success')
        except Exception as e:
            print(f"Chyba při odesílání e-mailu: {e}")
            flash('Odeslání zprávy selhalo. Zkuste to prosím znovu později.', 'error')

        return redirect(url_for('views.kontakt'))

    return render_template('kontakt.html')


@views.route("/inquiries")
def list_inquiries():
    inquiries = Inquiry.query.all()
    return render_template("list_inquiries.html", inquiries=inquiries)

@views.route("/register", methods=["GET", "POST"])
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
            return redirect(url_for("views.register"))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("E-mail je již používán. Zvolte jiný.", "error")
            return redirect(url_for("views.register"))

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(username=username, email=email, password=hashed_password, role='user')  # Role je nastavená na 'user'
        
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash("Registrace proběhla úspěšně. Nyní jste přihlášen/a.", "success")
        return redirect(url_for("views.home"))

    return render_template("register.html")


@views.route("/login", methods=["GET", "POST"])
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
        else:
            flash("Neplatné přihlašovací údaje!", "error")

    return render_template("login.html")



@views.route("/logout")
@login_required
def logout():
    """Odhlásí uživatele a přesměruje ho na homepage."""
    logout_user()  # Flask-Login funkce, zruší session pro daného uživatele
    flash("Byl jste úspěšně odhlášen.", "info")
    return redirect(url_for("views.home"))


@cart.route("/add", methods=["POST"])
@login_required
def add_to_cart():
    """Přidá produkt do košíku (nebo zvýší množství)"""
    data = request.get_json()
    product_id = data.get("product_id")

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Produkt nenalezen"}), 404

    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if cart_item:
        cart_item.quantity += 1  # Zvýší množství
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=1)
        db.session.add(cart_item)

    db.session.commit()
    return jsonify({"message": "Produkt přidán do košíku"}), 200

@cart.route("/remove", methods=["POST"])
@login_required
def remove_from_cart():
    """Odebere produkt z košíku"""
    data = request.get_json()
    product_id = data.get("product_id")

    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if not cart_item:
        return jsonify({"error": "Produkt není v košíku"}), 404

    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({"message": "Produkt odebrán z košíku"}), 200

@cart.route("/view", methods=["GET"])
@login_required
def view_cart():
    """Vrátí obsah košíku pro přihlášeného uživatele"""
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

    cart_data = [
        {
            "id": item.id,
            "product_id": item.product.id,
            "name": item.product.name,
            "price": item.product.price,
            "quantity": item.quantity,
            "total_price": item.product.price * item.quantity
        }
        for item in cart_items
    ]

    return jsonify(cart_data), 200

@views.route("/profil", methods=["GET", "POST"])
@login_required
def profil():
    if request.method == "POST":
        current_user.first_name = request.form.get("first_name")
        current_user.last_name = request.form.get("last_name")
        current_user.phone = request.form.get("phone")
        current_user.address = request.form.get("address")
        current_user.billing_address = request.form.get("billing_address")
        current_user.city = request.form.get("city")
        current_user.postal_code = request.form.get("postal_code")
        current_user.country = request.form.get("country")
        current_user.company = request.form.get("company")
        current_user.ico = request.form.get("ico")
        current_user.dic = request.form.get("dic")
        current_user.note = request.form.get("note")

        birth_date_str = request.form.get("birth_date")
        if birth_date_str:
            try:
                current_user.birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
            except ValueError:
                flash("Neplatný formát data narození (očekáváno RRRR-MM-DD)", "danger")

        db.session.commit()
        flash("Profil byl aktualizován.", "success")
        return redirect(url_for("views.profil"))

    return render_template("profil.html", user=current_user)

