from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from datetime import datetime
from pytz import timezone, UTC
from app import db, bcrypt, mail
from app.models import User, Product, Inquiry, CartItem, Order
from app.forms.forms import ProfileForm
from app.pdf_generator import generate_invoice_pdf

# Blueprints
views = Blueprint("views", __name__)
cart = Blueprint("cart", __name__, url_prefix="/cart")

# ---------- DOMOVSKÁ STRÁNKA ----------
@views.route("/", methods=["GET"])
def home():
    return render_template("home.html")

# ---------- GALERIE ----------
@views.route("/galerie")
def galerie():
    products = Product.query.filter(Product.is_active == True, Product.stock > 0).all()
    return render_template("galerie.html", products=products)

# ---------- KONTAKTNÍ FORMULÁŘ ----------
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

# ---------- VÝPIS DOTAZŮ ----------
@views.route("/inquiries")
def list_inquiries():
    inquiries = Inquiry.query.all()
    return render_template("list_inquiries.html", inquiries=inquiries)

# ---------- REGISTRACE ----------
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
        new_user = User(username=username, email=email, password=hashed_password, role='user')

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash("Registrace proběhla úspěšně. Nyní jste přihlášen/a.", "success")
        return redirect(url_for("views.home"))

    return render_template("register.html")

# ---------- PŘIHLÁŠENÍ ----------
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

# ---------- ODHLÁŠENÍ ----------
@views.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Byl jste úspěšně odhlášen.", "info")
    return redirect(url_for("views.home"))

# ---------- PROFIL ----------
@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        form.populate_obj(current_user)
        db.session.commit()
        flash("Profil byl úspěšně uložen.", "success")
        return redirect(url_for('views.profile'))
    return render_template('profile.html', form=form)

# ---------- KOŠÍK ----------
@cart.route("/add", methods=["POST"])
@login_required
def add_to_cart():
    data = request.get_json()
    product_id = data.get("product_id")

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Produkt nenalezen"}), 404

    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=1)
        db.session.add(cart_item)

    db.session.commit()
    return jsonify({"message": "Produkt přidán do košíku"}), 200

@cart.route("/remove", methods=["POST"])
@login_required
def remove_from_cart():
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

# ---------- MOJE OBJEDNÁVKY ----------
@views.route("/moje-objednavky")
@login_required
def moje_objednavky():
    orders = current_user.orders
    order_data = []
    for order in orders:
        client_tz = timezone(order.timezone or 'UTC')
        local_time = order.created_at.replace(tzinfo=UTC).astimezone(client_tz)
        order_data.append((order, local_time))
    return render_template("moje_objednavky.html", order_data=order_data)

@views.route("/objednavka/<int:order_id>")
@login_required
def detail_objednavky(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first()
    if not order:
        flash("Objednávka nebyla nalezena.", "warning")
        return redirect(url_for("views.moje_objednavky"))

    client_tz = timezone(order.timezone or 'UTC')
    local_time = order.created_at.replace(tzinfo=UTC).astimezone(client_tz)
    return render_template("detail_objednavky.html", order=order, local_time=local_time)

# ---------- FAKTURA PDF ----------
@views.route("/objednavka/<int:order_id>/faktura")
@login_required
def stahnout_fakturu(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first()
    if not order:
        flash("Objednávka nebyla nalezena.", "warning")
        return redirect(url_for("views.moje_objednavky"))

    pdf_buffer = generate_invoice_pdf(order)
    return send_file(pdf_buffer, mimetype="application/pdf", as_attachment=True,
                     download_name=f"faktura_{order.invoice_number}.pdf")

# ---------- POSLAT FAKTURU EMAILEM ----------
@views.route("/objednavka/<int:order_id>/faktura/email")
@login_required
def poslat_fakturu_emailem(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first()
    if not order:
        flash("Objednávka nebyla nalezena.", "warning")
        return redirect(url_for("views.moje_objednavky"))

    pdf_buffer = generate_invoice_pdf(order)
    msg = Message(subject=f"📎 Faktura č. {order.invoice_number}",
                  sender="info@tvujeshop.cz",
                  recipients=[current_user.email],
                  body=f"Dobrý den,\npřikládáme fakturu k vaší objednávce č. {order.invoice_number}.\nDěkujeme za nákup.")
    msg.attach(f"faktura_{order.invoice_number}.pdf", "application/pdf", pdf_buffer.read())
    mail.send(msg)
    flash("Faktura byla odeslána na váš e-mail.", "success")
    return redirect(url_for("views.moje_objednavky"))
