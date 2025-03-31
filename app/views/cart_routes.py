from flask import Blueprint, request, jsonify, render_template, session
from flask_login import login_required, current_user
from app.models import Product, CartItem
from app import db

cart = Blueprint("cart", __name__, url_prefix="/cart")

# Funkce pro aktualizaci počtu položek v košíku
def update_cart_count():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    session['cart_item_count'] = sum(item.quantity for item in cart_items)

# Přidání produktu do košíku
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

    # Kontrola skladu
    if product.stock <= 0:
        return jsonify({'message': 'Produkt není skladem.'}), 400

    existing_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if existing_item:
        if existing_item.quantity < product.stock:
            existing_item.quantity += 1
        else:
            return jsonify({'message': 'Nelze přidat více kusů, než je skladem.'}), 400
    else:
        new_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=1)
        db.session.add(new_item)

    db.session.commit()
    return jsonify({'message': f'Produkt {product.name} byl přidán do košíku.'}), 200




# Odebrání produktu z košíku
@cart.route('/remove', methods=['POST'])
@login_required
def remove_from_cart():
    data = request.get_json()
    product_id = data.get('product_id')

    if not product_id:
        return jsonify({"error": "Produkt nebyl specifikován."}), 400

    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if not cart_item:
        return jsonify({"error": "Produkt není v košíku."}), 404

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
    else:
        db.session.delete(cart_item)

    db.session.commit()
    return jsonify({"message": "Produkt byl úspěšně odstraněn z košíku."}), 200


# Zobrazení košíku
@cart.route('/view', methods=['GET'])
@login_required
def view_cart():
    # Odstranění osamocených položek před zobrazením košíku
    orphaned_items = CartItem.query.filter(~CartItem.product.has()).all()
    for item in orphaned_items:
        db.session.delete(item)
    db.session.commit()

    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render_template('cart.html', cart_items=cart_items, total_price=total_price)


# Route pro počet položek v košíku
@cart.route('/count', methods=['GET'])
@login_required
def cart_count():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    cart_item_count = sum(item.quantity for item in cart_items)
    return jsonify({'cart_item_count': cart_item_count})
