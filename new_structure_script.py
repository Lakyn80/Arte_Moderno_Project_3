import os

# Cílová složka pro nové rozdělené routy
target_folder = "app/routes"
os.makedirs(target_folder, exist_ok=True)

# Definice názvů a hlaviček souborů + příslušné routy (modulárně)
modules = {
    "views_routes.py": {
        "blueprint": "views = Blueprint('views', __name__)",
        "routes": [
            "home", "galerie", "kontakt", "list_inquiries"
        ]
    },
    "auth_routes.py": {
        "blueprint": "auth = Blueprint('auth', __name__)",
        "routes": [
            "register", "login", "logout", "client_reset_request", "client_reset_token"
        ]
    },
    "profile_routes.py": {
        "blueprint": "profile = Blueprint('profile', __name__)",
        "routes": ["profil"]
    },
    "cart_routes.py": {
        "blueprint": "cart = Blueprint('cart', __name__, url_prefix='/cart')",
        "routes": [
            "add_to_cart", "remove_one_from_cart", "remove_all_from_cart",
            "view_cart", "apply_discount", "remove_discount", "cart_count"
        ]
    },
    "checkout_routes.py": {
        "blueprint": "checkout = Blueprint('checkout', __name__, url_prefix='/checkout')",
        "routes": ["checkout_summary", "confirm_order"]
    },
    "orders_routes.py": {
        "blueprint": "orders = Blueprint('orders', __name__)",
        "routes": [
            "moje_objednavky", "detail_objednavky", "stahnout_fakturu", "poslat_fakturu_emailem"
        ]
    },
    "language_routes.py": {
        "blueprint": "language = Blueprint('language', __name__)",
        "routes": ["set_language"]
    },
    "admin_routes.py": {
        "blueprint": "admin = Blueprint('admin', __name__, url_prefix='/admin')",
        "routes": [
            "dashboard", "add_product", "edit_product", "delete_product", "reactivate_product",
            "hard_delete_product", "admin_login", "admin_change_password", "admin_reset_request",
            "admin_reset_token", "export_orders_csv", "admin_orders", "order_detail",
            "update_order_status", "update_order_note", "user_detail", "manage_discounts",
            "restore_order_for_user", "hide_order_from_user"
        ]
    }
}

# Vytvoření prázdných souborů s hlavičkami
for filename, content in modules.items():
    path = os.path.join(target_folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write("from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, current_app, send_file\n")
        f.write("from flask_login import login_user, current_user, logout_user, login_required\n")
        f.write("from flask_mail import Message\n")
        f.write("from datetime import datetime\n")
        f.write("from pytz import timezone, UTC\n")
        f.write("from app import db, bcrypt, mail\n")
        f.write("from app.models import User, Product, Inquiry, CartItem, Order, OrderItem, DiscountCode\n")
        f.write("from app.forms.forms import ProfileForm, ContactForm, ClientResetRequestForm, ClientResetPasswordForm\n")
        f.write("from app.forms.admin_forms import AdminLoginForm, AdminChangePasswordForm, AdminResetRequestForm, AdminResetPasswordForm, AdminUpdateOrderStatusForm, AdminUpdateOrderNoteForm, AdminDiscountForm\n")
        f.write("from app.utils import generate_invoice_number\n")
        f.write("from app.pdf_generator import generate_invoice_pdf\n")
        f.write("from sqlalchemy.orm import joinedload\n")
        f.write("from functools import wraps\n")
        f.write("from werkzeug.utils import secure_filename\n")
        f.write("import os, csv\n")
        f.write("from io import StringIO\n")
        f.write("from flask import make_response\n")
        f.write(f"{content['blueprint']}\n\n")
        f.write("# ROUTY ZDE BUDOU VLOŽENY RUČNĚ DLE FUNKCÍ\n")

target_folder
