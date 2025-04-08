from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.models import Product, CartItem, DiscountCode

cart = Blueprint("cart", __name__, url_prefix="/cart")


def update_cart_count():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    session['cart_item_count'] = sum(item.quantity for item in cart_items)


@cart.route('/add', methods=['POST'])
@login_required
def add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')

    if not product_id:
        return jsonify({'message': 'Produkt nebyl nalezen.'}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Produkt neexistuje.'}), 404

    if product.stock <= 0:
        return jsonify({'message': 'Produkt není skladem.'}), 400

    existing_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if existing_item:
        if existing_item.quantity < product.stock:
            existing_item.quantity += 1
            product.stock -= 1
        else:
            return jsonify({'message': 'Nelze přidat více kusů, než je skladem.'}), 400
    else:
        new_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=1)
        db.session.add(new_item)
        product.stock -= 1

    if product.stock <= 0:
        product.is_active = False

    db.session.commit()
    update_cart_count()
    return jsonify({'message': f'Produkt {product.name} byl přidán do košíku.'}), 200


@cart.route('/remove_one', methods=['POST'])
@login_required
def remove_one_from_cart():
    data = request.get_json()
    product_id = data.get("product_id")

    if not product_id:
        return jsonify({"error": "Produkt nebyl specifikován."}), 400

    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if not cart_item:
        return jsonify({"error": "Produkt není v košíku."}), 404

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Produkt nebyl nalezen."}), 404

    product.stock += 1
    product.is_active = True

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
    else:
        db.session.delete(cart_item)

    db.session.commit()
    update_cart_count()
    return jsonify({"message": "Odebrán jeden kus produktu z košíku."}), 200


@cart.route('/remove_all', methods=['POST'])
@login_required
def remove_all_from_cart():
    data = request.get_json()
    product_id = data.get("product_id")

    if not product_id:
        return jsonify({"error": "Produkt nebyl specifikován."}), 400

    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if not cart_item:
        return jsonify({"error": "Produkt není v košíku."}), 404

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Produkt nebyl nalezen."}), 404

    product.stock += cart_item.quantity
    product.is_active = True

    db.session.delete(cart_item)
    db.session.commit()
    update_cart_count()

    return jsonify({"message": "Celý produkt byl odebrán z košíku."}), 200


@cart.route('/view', methods=['GET'])
@login_required
def view_cart():
    orphaned_items = CartItem.query.filter(~CartItem.product.has()).all()
    for item in orphaned_items:
        db.session.delete(item)
    db.session.commit()

    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    discount_percent = session.get("discount_percent")
    if discount_percent:
        total_price = total_price * (1 - discount_percent / 100)

    return render_template("client/cart.html", cart_items=cart_items, total_price=round(total_price, 2))


@cart.route('/apply_discount', methods=['POST'])
@login_required
def apply_discount():
    code = request.form.get("discount_code", "").strip().lower()
    discount = DiscountCode.query.filter(func.lower(DiscountCode.code) == code).first()

    if not discount:
        session["discount_error"] = "Slevový kód neexistuje."
        session.pop("discount_percent", None)
    elif not discount.is_valid():
        session["discount_error"] = "Slevový kód je neplatný nebo expirovaný."
        session.pop("discount_percent", None)
    else:
        session["discount_success"] = True
        session["discount_percent"] = discount.discount_percent
        session.pop("discount_error", None)

    return redirect(url_for('cart.view_cart'))


@cart.route('/count', methods=['GET'])
@login_required
def cart_count():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    cart_item_count = sum(item.quantity for item in cart_items)
    return jsonify({'cart_item_count': cart_item_count})


@cart.route('/remove_discount', methods=['POST'])
@login_required
def remove_discount():
    session.pop("discount_percent", None)
    session.pop("discount_success", None)
    session.pop("discount_error", None)
    flash("Slevový kód byl odebrán.", "info")
    return redirect(request.referrer or url_for('cart.view_cart'))
