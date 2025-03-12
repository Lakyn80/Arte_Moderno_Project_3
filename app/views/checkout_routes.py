# app/views/checkout_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import CartItem, Product, Order, OrderItem
from app import db, mail
from flask_mail import Message

checkout = Blueprint("checkout", __name__, url_prefix="/checkout")


@checkout.route("/summary", methods=["GET"])
@login_required
def checkout_summary():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash("Košík je prázdný.", "warning")
        return redirect(url_for("cart.view_cart"))

    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render_template("checkout_success.html", cart_items=cart_items, total_price=total_price)


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

    # Uložení objednávky
    order = Order(user_id=current_user.id, total_price=total_price,
                  address=address, billing_address=billing_address)
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

        item.product.stock -= item.quantity
        if item.product.stock <= 0:
            item.product.is_active = False

    db.session.query(CartItem).filter_by(user_id=current_user.id).delete()
    db.session.commit()

    # E-mail firmě
    try:
        admin_msg = Message("📦 Nová objednávka",
                            sender="noreply@artemoderno.cz",
                            recipients=["artemodernoblaha@gmail.com"])
        msg_body = f"Uživatel {current_user.username} ({current_user.email}) provedl objednávku.\n\n"
        msg_body += f"Adresa: {address}\nFakturační adresa: {billing_address}\n\n"
        for item in cart_items:
            msg_body += f"{item.product.name} – {item.quantity} ks × {item.product.price} Kč\n"
        msg_body += f"\nCelková cena: {total_price} Kč"
        admin_msg.body = msg_body
        mail.send(admin_msg)

        # E-mail zákazníkovi
        client_msg = Message("✅ Vaše objednávka byla přijata",
                             sender="artemodernoblaha@gmail.com",
                             recipients=[current_user.email])
        client_msg.body = f"Dobrý den {current_user.username},\n\nděkujeme za vaši objednávku.\n\n" + msg_body
        mail.send(client_msg)

    except Exception as e:
        print("Chyba při odesílání e-mailu:", e)

    flash("Objednávka byla úspěšně odeslána!", "success")
    return redirect(url_for("views.home"))
