from datetime import datetime
from flask_login import UserMixin
from flask import url_for

from app.extensions import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))


    # PROFIL – volitelné údaje
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    phone = db.Column(db.String(32), nullable=True)
    address = db.Column(db.Text, nullable=True)
    billing_address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(64), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    country = db.Column(db.String(64), nullable=True)
    company = db.Column(db.String(128), nullable=True)
    company_id = db.Column(db.String(32), nullable=True)  # IČO
    vat_id = db.Column(db.String(32), nullable=True)      # DIČ
    note = db.Column(db.Text, nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)

    # RELACE
    cart_items = db.relationship('CartItem', backref='user', lazy=True)
    orders = db.relationship('Order', back_populates='user', lazy=True)


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    image_filename = db.Column(db.String(256), nullable=True)
    stock = db.Column(db.Integer, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    position_id = db.Column(db.Integer, nullable=True)


    def get_image_url(self):
        if self.image_filename:
            return url_for('static', filename='uploads/' + self.image_filename)
        return url_for('static', filename='images/default_product.jpg')


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    product = db.relationship('Product', backref='cart_items')


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_per_item = db.Column(db.Float, nullable=False)

    product = db.relationship('Product', backref='order_items', lazy=True)
    order = db.relationship('Order', back_populates='items')


class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='new')
    invoice_number = db.Column(db.String(32), unique=True, nullable=True)
    timezone = db.Column(db.String(64), nullable=True)
    address = db.Column(db.Text, nullable=True)
    billing_address = db.Column(db.Text, nullable=True)
    note = db.Column(db.Text)  # ✅ přidaný sloupec

    user = db.relationship("User", back_populates="orders")
    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
