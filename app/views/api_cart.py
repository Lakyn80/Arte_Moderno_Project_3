from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import Product, CartItem
from app.extensions import db


api_cart = Blueprint("api_cart", __name__, url_prefix="/api/cart")


@api_cart.route("/add", methods=["POST"])
@login_required
def api_add_to_cart():
    from app import db  # <- TADY uvnitř funkce
    data = request.get_json()
    product_id = data.get("product_id")

    if not product_id:
        return jsonify({"error": "Produkt nebyl zadán."}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Produkt nenalezen."}), 404

    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=1)
        db.session.add(cart_item)

    db.session.commit()
    return jsonify({"message": "Produkt přidán do košíku."}), 200


@api_cart.route("/remove", methods=["POST"])
@login_required
def api_remove_from_cart():
    from app import db  # <- TADY
    data = request.get_json()
    product_id = data.get("product_id")

    if not product_id:
        return jsonify({"error": "Produkt nebyl zadán."}), 400

    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if not cart_item:
        return jsonify({"error": "Produkt není v košíku."}), 404

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
    else:
        db.session.delete(cart_item)

    db.session.commit()
    return jsonify({"message": "Produkt odebrán z košíku."}), 200


@api_cart.route("/view", methods=["GET"])
@login_required
def api_view_cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    cart_data = [
        {
            "product_id": item.product.id,
            "name": item.product.name,
            "price": item.product.price,
            "quantity": item.quantity,
            "total_price": item.product.price * item.quantity
        }
        for item in cart_items
    ]
    return jsonify(cart_data), 200
