from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Product, Inquiry

views = Blueprint("views", __name__)

# ---------- DOMOVSKÁ STRÁNKA ----------
@views.route("/", methods=["GET"])
def home():
    return render_template("base_html_section/home.html")

# ---------- GALERIE ----------
@views.route("/galerie")
def galerie():
    products = Product.query.filter(Product.is_active == True, Product.stock > 0).all()
    return render_template("client/galerie.html", products=products)

# ---------- KONTAKTNÍ FORMULÁŘ ----------
@views.route("/kontakt", methods=["GET", "POST"])
def kontakt():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject') or 'Bez předmětu'
        message = request.form.get('message')

        try:
            from flask_mail import Message
            from app import mail

            owner_msg = Message(
                subject=f"Nová zpráva od {name} - {subject}",
                sender=email,
                recipients=['artemodernoblaha@gmail.com'],
                body=f"Od: {name} <{email}>\n\n{message}"
            )
            mail.send(owner_msg)

            confirmation_msg = Message(
                subject="Děkujeme za vaši zprávu",
                sender='artemodernoblaha@gmail.com',
                recipients=[email],
                body=f"Dobrý den {name},\n\nDěkujeme za vaši zprávu. Odpovíme vám co nejdříve.\n\nVaše zpráva:\n{message}\n\nS pozdravem,\nArte Moderno"
            )
            mail.send(confirmation_msg)

            flash('Zpráva byla úspěšně odeslána! Potvrzení bylo zasláno na váš e-mail.', 'success')
        except Exception as e:
            print(f"Chyba při odesílání e-mailu: {e}")
            flash('Odeslání zprávy selhalo. Zkuste to prosím znovu později.', 'error')

        return redirect(url_for('views.kontakt'))

    return render_template('client/kontakt.html')

# ---------- VÝPIS DOTAZŮ ----------
@views.route("/inquiries")
def list_inquiries():
    inquiries = Inquiry.query.all()
    return render_template("client/list_inquiries.html", inquiries=inquiries)
