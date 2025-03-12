# app/views/checkout_routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import CartItem, Product, Order, OrderItem
from app import db, mail
from flask_mail import Message

checkout = Blueprint("checkout", __name__, url_prefix="/checkout")

@checkout.route("/summary", methods=["GET"])
@login_required
def checkout_summary():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render_template("checkout_success.html", cart_items=cart_items, total_price=total_price)


@checkout.route("/confirm", methods=["POST"])
@login_required
def confirm_order():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash("Košík je prázdný.", "warning")
        return redirect(url_for("cart.view_cart"))

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    address = request.form.get("address")
    billing_address = request.form.get("billing_address")

    # Vytvoření objednávky
    order = Order(
        user_id=current_user.id,
        total_price=total_price,
        address=address,
        billing_address=billing_address
    )
    db.session.add(order)
    db.session.flush()

    order_items_text = ""
    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_per_item=item.product.price
        )
        db.session.add(order_item)

        order_items_text += f"{item.product.name} – {item.quantity} ks × {item.product.price} Kč = {item.quantity * item.product.price} Kč\n"

        item.product.stock -= item.quantity
        if item.product.stock <= 0:
            item.product.is_active = False

    # Vymazání košíku
    for item in cart_items:
        db.session.delete(item)

    db.session.commit()

    # 📧 Odeslání e-mailu firmě
    try:
        msg_owner = Message(
            subject="📥 Nová objednávka",
            sender="artemodernoblaha@gmail.com",
            recipients=["artemodernoblaha@gmail.com"],
            body=f"""Nová objednávka od {current_user.username} ({current_user.email}):

Doručovací adresa:
{address}

Fakturační adresa:
{billing_address or 'Neuvedena'}

Položky:
{order_items_text}

Celková cena: {total_price} Kč
"""
        )
        mail.send(msg_owner)

        # 📧 Odeslání e-mailu zákazníkovi
        msg_customer = Message(
            subject="✅ Potvrzení objednávky – ArteModerno",
            sender="artemodernoblaha@gmail.com",
            recipients=[current_user.email],
            body=f"""Dobrý den {current_user.username},

děkujeme za vaši objednávku. Zde je rekapitulace:

Položky:
{order_items_text}

Doručovací adresa:
{address}

Fakturační adresa:
{billing_address or 'Neuvedena'}

Celková cena: {total_price} Kč

Brzy vás budeme kontaktovat ohledně doručení.
S pozdravem,
ArteModerno tým
"""
        )
        mail.send(msg_customer)

    except Exception as e:
        print(f"Chyba při odesílání e-mailů: {e}")

    flash("Objednávka byla potvrzena a e-maily byly odeslány.", "success")
    return redirect(url_for("views.home"))
