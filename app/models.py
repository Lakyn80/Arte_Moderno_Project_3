import os
from flask_login import UserMixin
from datetime import datetime
from app import db

# --------------------
# Uživatelský model
# --------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.username}>"

# --------------------
# Dotazy (kontaktní formulář)
# --------------------
class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(150))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Inquiry from {self.name}, {self.email}>"

# --------------------
# Produkty (např. obrazy) s podporou soft deletion
# --------------------
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    position_id = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    image_filename = db.Column(db.String(300), nullable=True)
    stock = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, default=True, nullable=False)  # Příznak aktivity produktu
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_image_url(self):
        if self.image_filename:
            return f"/static/uploads/{self.image_filename}"
        return "/static/images/placeholder.png"

    def __repr__(self):
        return f"<Product {self.name}, Position {self.position_id}>"

# --------------------
# Položky v košíku
# --------------------
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete="CASCADE"), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)

    product = db.relationship('Product', backref=db.backref('cart_items', cascade='all, delete'))

    def __repr__(self):
        return f"<CartItem User {self.user_id}, Product {self.product_id}, Qty {self.quantity}>"

# --------------------
# Objednávky (checkout)
# --------------------
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False, default='pending')

    user = db.relationship('User', backref=db.backref('orders', lazy=True))

    def __repr__(self):
        return f"<Order #{self.id} - User {self.user_id} - {self.status}>"

# --------------------
# Položky objednávky
# --------------------
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_per_item = db.Column(db.Float, nullable=False)

    order = db.relationship('Order', backref=db.backref('items', lazy=True))
    product = db.relationship('Product')

    def __repr__(self):
        return f"<OrderItem Order {self.order_id} - Product {self.product_id} - Qty {self.quantity}>"
