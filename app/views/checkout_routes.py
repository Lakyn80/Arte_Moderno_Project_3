# app/views/checkout_routes.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import CartItem, Product, Order, OrderItem
from app import db

checkout = Blueprint("checkout", __name__, url_prefix="/checkout")

@checkout.route('/', methods=['GET', 'POST'])
@login_required
def process_checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

    if not cart_items:
        flash("Košík je prázdný.", "warning")
        return redirect(url_for('cart.view_cart'))

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    # Vytvoření objednávky
    order = Order(user_id=current_user.id, total_price=total_price)
    db.session.add(order)
    db.session.flush()  # získáme order.id bez commitu

    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_per_item=item.product.price
        )
        db.session.add(order_item)

        # Snížení skladu a případná deaktivace, pokud je vyprodán
        item.product.stock -= item.quantity
        if item.product.stock <= 0:
            item.product.is_active = False

    # Vymazání košíku
    for item in cart_items:
        db.session.delete(item)

    db.session.commit()
    flash("Objednávka byla úspěšně vytvořena!", "success")
    return render_template("checkout_success.html", order=order)

