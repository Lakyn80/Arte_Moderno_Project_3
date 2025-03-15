# app/views/checkout_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_mail import Message
from datetime import datetime

from app import db, mail
from app.models import CartItem, Product, Order, OrderItem
from app.utils import generate_order_number  # ✅ použijeme z utils.py

checkout = Blueprint("checkout", __name__, url_prefix="/checkout")


# ---------- Rekapitulace objednávky ----------
@checkout.route("/summary", methods=["GET"])
@login_required
def checkout_summary():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash("Košík je prázdný.", "warning")
        return redirect(url_for("cart.view_cart"))

    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render_template("checkout_success.html", cart_items=cart_items, total_price=total_price)


# ---------- Potvrzení objednávky ----------
@checkout.route("/confirm", methods=["POST"])
@login_required
def confirm_order():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash("Košík je prázdný.", "warning")
        return redirect(url_for("cart.view_cart"))

    address = request.form.get("address")
    billing_address = request.form.get("billing_address")

    if not address:
        flash("Doručovací adresa je povinná.", "danger")
        return redirect(url_for("checkout.checkout_summary"))

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    order = Order(
        user_id=current_user.id,
        total_price=total_price,
        created_at=datetime.utcnow(),
        address=address,
        billing_address=billing_address,
        order_number=generate_order_number()
    )
    db.session.add(order)
    db.session.flush()

    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_per_item=item.product.price
        )
        db.session.add(order_item)

        # Snížení skladu
        item.product.stock -= item.quantity
        if item.product.stock <= 0:
            item.product.is_active = False

    # Vyprázdnění košíku
    db.session.query(CartItem).filter_by(user_id=current_user.id).delete()
    db.session.commit()

    # E-maily
    try:
        admin_msg = Message("📦 Nová objednávka",
                            sender="noreply@artemoderno.cz",
                            recipients=["artemodernoblaha@gmail.com"])
        msg_body = f"Nová objednávka číslo {order.order_number}\n"
        msg_body += f"Zákazník: {current_user.username} ({current_user.email})\n"
        msg_body += f"Doručovací adresa: {address}\nFakturační adresa: {billing_address}\n\n"
        for item in cart_items:
            msg_body += f"{item.product.name} – {item.quantity} ks × {item.product.price:.2f} Kč\n"
        msg_body += f"\nCelková cena: {total_price:.2f} Kč"

        admin_msg.body = msg_body
        mail.send(admin_msg)

        client_msg = Message("✅ Vaše objednávka byla přijata",
                             sender="artemodernoblaha@gmail.com",
                             recipients=[current_user.email])
        client_msg.body = f"Dobrý den {current_user.username},\n\nděkujeme za vaši objednávku.\n\n" + msg_body
        mail.send(client_msg)

    except Exception as e:
        print("Chyba při odesílání e-mailu:", e)

    flash(f"Objednávka byla úspěšně odeslána! Číslo objednávky: {order.order_number}", "success")
    return redirect(url_for("views.moje_objednavky"))
