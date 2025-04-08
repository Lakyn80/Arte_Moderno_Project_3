from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from flask_mail import Message
from app.utils import generate_invoice_number
from app import db, mail
from app.models import CartItem, Product, Order, OrderItem

checkout = Blueprint("checkout", __name__)


# ---------- Rekapitulace objednávky ----------
@checkout.route("/checkout/summary", methods=["GET"])
@login_required
def checkout_summary():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash("Košík je prázdný.", "warning")
        return redirect(url_for("cart.view_cart"))

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    # Sleva ze session
    discount_percent = session.get("discount_percent")
    discount_amount = 0
    if discount_percent:
        discount_amount = total_price * (discount_percent / 100)
        total_price -= discount_amount

    return render_template(
        "client/checkout_summary.html",
        cart_items=cart_items,
        total_price=round(total_price, 2),
        discount_percent=discount_percent,
        discount_amount=round(discount_amount, 2)
    )


# ---------- Potvrzení objednávky ----------
@checkout.route("/checkout/confirm", methods=["POST"])
@login_required
def confirm_order():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash("Košík je prázdný.", "warning")
        return redirect(url_for("cart.view_cart"))

    address = request.form.get("address")
    billing_address = request.form.get("billing_address")
    timezone_client = request.form.get("timezone")

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    # Sleva (znovu aplikuj pro jistotu)
    discount_percent = session.get("discount_percent")
    if discount_percent:
        total_price = total_price * (1 - discount_percent / 100)

    invoice_number = generate_invoice_number()

    # ✅ 1. Uložení objednávky
    order = Order(
        user_id=current_user.id,
        total_price=round(total_price, 2),
        address=address,
        billing_address=billing_address,
        invoice_number=invoice_number,
        timezone=timezone_client
    )
    db.session.add(order)
    db.session.flush()

    # ✅ 2. Uložení položek + aktualizace skladu
    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_per_item=item.product.price
        )
        db.session.add(order_item)

        item.product.stock -= item.quantity
        if item.product.stock <= 0:
            item.product.is_active = False

    # Smazání položek z košíku
    db.session.query(CartItem).filter_by(user_id=current_user.id).delete()

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash("Nastala chyba při ukládání objednávky.", "error")
        print("Chyba při ukládání objednávky:", e)
        return redirect(url_for("cart.view_cart"))

    # ✅ 3. Odeslání e-mailů
    try:
        msg_body = f"Nová objednávka č. {invoice_number}\n"
        msg_body += f"Zákazník: {current_user.username} ({current_user.email})\n"
        msg_body += f"Doručovací adresa: {address}\nFakturační adresa: {billing_address}\n\n"
        for item in cart_items:
            msg_body += f"{item.product.name} – {item.quantity} ks × {item.product.price:.2f} Kč\n"
        msg_body += f"\nCelková cena: {total_price:.2f} Kč"

        admin_msg = Message(
            "📦 Nová objednávka",
            sender="noreply@artemoderno.cz",
            recipients=["artemodernoblaha@gmail.com"],
            body=msg_body
        )
        mail.send(admin_msg)

        client_msg = Message(
            "✅ Vaše objednávka byla přijata",
            sender="noreply@artemoderno.cz",
            recipients=[current_user.email],
            body=f"Dobrý den {current_user.username},\n\nDěkujeme za vaši objednávku.\n\n" + msg_body
        )
        mail.send(client_msg)

    except Exception as e:
        print("Chyba při odesílání e-mailu:", e)

    # ✅ 4. Vyčištění session od slev
    session.pop("discount_percent", None)
    session.pop("discount_success", None)
    session.pop("discount_error", None)

    flash(f"Objednávka byla odeslána! Faktura č. {invoice_number}", "success")
    return redirect(url_for("orders.moje_objednavky"))

