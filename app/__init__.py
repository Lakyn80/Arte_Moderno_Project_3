from flask import Flask, g, session, current_app
from flask_login import current_user
import json
import os

# 🔌 Rozšíření
from app.extensions import db, mail, bcrypt, login_manager, csrf, migrate

# 🧠 API blueprinty (musí být až po extensions)
from app.routes.cart_api_routes import api_cart

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # ✅ Inicializace rozšíření
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # 🔐 Login Manager – přihlášení pro klienty
    login_manager.login_view = "auth_client.login"
    login_manager.login_message_category = "info"

    # 🧠 Načtení modelů
    from app.models import User, CartItem

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 🛠️ CLI příkazy
    from app.commands import register_commands
    register_commands(app)

    # 🧩 Import a registrace všech blueprintů
    from app.routes.views_routes import views
    from app.routes.auth_admin_routes import auth_admin
    from app.routes.auth_client_routes import auth_client
    from app.routes.admin_routes import admin
    from app.routes.cart_routes import cart
    from app.routes.checkout_routes import checkout 
    from app.routes.orders_routes import orders
    from app.routes.language_routes import language
    from app.routes.profile_routes import profile

    app.register_blueprint(api_cart, url_prefix="/api/cart")
    app.register_blueprint(views)
    app.register_blueprint(auth_admin)
    app.register_blueprint(auth_client)
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(cart)
    app.register_blueprint(checkout)
    app.register_blueprint(orders)
    app.register_blueprint(language, url_prefix="/language")
    app.register_blueprint(profile)

    # 🛒 Kontextový procesor – počet položek v košíku
    @app.context_processor
    def inject_cart_count():
        if current_user.is_authenticated:
            cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
            cart_count = sum(item.quantity for item in cart_items)
        else:
            cart_count = 0
        return dict(cart_item_count=cart_count)

    # 🌐 Načtení překladů z JSON
    @app.before_request
    def load_translation():
        lang = session.get("lang", "cs")
        path = os.path.join(os.path.dirname(__file__), "static", "translation", f"{lang}.json")
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read().strip()
                g.t = json.loads(content) if content else {}
        except Exception as e:
            print("Překlad se nepodařilo načíst:", e)
            g.t = {}

    return app
