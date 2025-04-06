from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, send_file, current_app
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from datetime import datetime
from pytz import timezone, UTC
from itsdangerous import URLSafeTimedSerializer
from app import db, bcrypt, mail
from app.models import User, Product, Inquiry, CartItem, Order
from app.forms.forms import ProfileForm, ContactForm, ClientResetRequestForm, ClientResetPasswordForm
from app.pdf_generator import generate_invoice_pdf

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
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        subject = form.subject.data or 'Bez předmětu'
        message = form.message.data

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

    return render_template('kontakt.html', form=form)

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

# ---------- RESET HESLA ----------
@views.route("/reset_password", methods=["GET", "POST"])
def client_reset_request():
    form = ClientResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data, role='user').first()
        if user:
            serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
            token = serializer.dumps(user.email, salt="user-reset-salt")
            reset_url = url_for("views.client_reset_token", token=token, _external=True)

            msg = Message("Obnova hesla – ArteModerno",
                          sender="noreply@artemoderno.cz",
                          recipients=[user.email])
            msg.body = f"""Dobrý den,

pro změnu hesla klikněte na tento odkaz (platí 30 minut):
{reset_url}

Pokud jste žádost neodesílali, ignorujte tento e-mail.
"""
            mail.send(msg)
            flash("Odkaz na obnovu hesla byl odeslán na váš e-mail.", "info")
            return redirect(url_for("views.login"))
        else:
            flash("Uživatel s tímto e-mailem nebyl nalezen.", "warning")
    return render_template("client_reset_request.html", form=form)

@views.route("/reset_password/<token>", methods=["GET", "POST"])
def client_reset_token(token):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = serializer.loads(token, salt="user-reset-salt", max_age=1800)
    except Exception:
        flash("Odkaz je neplatný nebo vypršel.", "danger")
        return redirect(url_for("views.client_reset_request"))

    user = User.query.filter_by(email=email, role='user').first()
    if not user:
        flash("Uživatel nebyl nalezen.", "danger")
        return redirect(url_for("views.client_reset_request"))

    form = ClientResetPasswordForm()
    if form.validate_on_submit():
        user.password = bcrypt.generate_password_hash(form.new_password.data).decode("utf-8")
        db.session.commit()
        flash("Heslo bylo úspěšně změněno. Nyní se můžete přihlásit.", "success")
        return redirect(url_for("views.login"))

    return render_template("client_reset_password.html", form=form)

# ---------- PROFIL ----------
@views.route("/profil", methods=["GET", "POST"])
@login_required
def profil():
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        current_user.billing_address = form.billing_address.data
        current_user.city = form.city.data
        current_user.postal_code = form.postal_code.data
        current_user.country = form.country.data
        current_user.company = form.company.data
        current_user.company_id = form.company_id.data
        current_user.vat_id = form.vat_id.data
        current_user.note = form.note.data
        current_user.date_of_birth = form.date_of_birth.data

        db.session.commit()
        flash("✅ Profil byl úspěšně uložen.", "success")
        return redirect(url_for("views.profil"))

    return render_template("profil.html", form=form, birthdate=current_user.date_of_birth, datetime=datetime)



# ---------- KOŠÍK ----------
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

# ---------- OBJEDNÁVKY ----------
@views.route("/moje-objednavky")
@login_required
def moje_objednavky():
    orders = Order.query.filter_by(user_id=current_user.id, visible_to_user=True).order_by(Order.created_at.desc()).all()
    order_data = []
    for order in orders:
        client_tz = timezone(order.timezone or 'UTC')
        local_time = order.created_at.replace(tzinfo=UTC).astimezone(client_tz)
        order_data.append((order, local_time))

    return render_template("moje_objednavky.html", order_data=order_data)

@views.route("/objednavka/<int:order_id>")
@login_required
def detail_objednavky(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id, visible_to_user=True).first()
    if not order:
        flash("Objednávka nebyla nalezena nebo byla skryta administrátorem.", "warning")
        return redirect(url_for("views.moje_objednavky"))

    client_tz = timezone(order.timezone or 'UTC')
    local_time = order.created_at.replace(tzinfo=UTC).astimezone(client_tz)
    return render_template("detail_objednavky.html", order=order, local_time=local_time)

@views.route("/objednavka/<int:order_id>/faktura")
@login_required
def stahnout_fakturu(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id, visible_to_user=True).first()
    if not order:
        flash("Faktura není dostupná. Objednávka byla možná skryta.", "warning")
        return redirect(url_for("views.moje_objednavky"))

    pdf_buffer = generate_invoice_pdf(order)
    return send_file(pdf_buffer, mimetype="application/pdf", as_attachment=True,
                     download_name=f"faktura_{order.invoice_number}.pdf")

@views.route("/objednavka/<int:order_id>/faktura/email")
@login_required
def poslat_fakturu_emailem(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id, visible_to_user=True).first()
    if not order:
        flash("Objednávka byla skryta a faktura není dostupná.", "warning")
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
