from flask import Flask
from flask_login import current_user

# Import rozšíření (pouze import z extensions)
from app.extensions import db, mail, bcrypt, login_manager, csrf, migrate

# Import API blueprints (musí být až po extensions!)
from app.views.api_cart import api_cart


def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # Inicializace rozšíření s aplikací
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Nastavení LoginManageru
    login_manager.login_view = "views.login"
    login_manager.login_message_category = "info"

    # Modely (až po init extensions)
    from app.models import User, CartItem

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # CLI příkazy
    from app.commands import register_commands
    register_commands(app)

    # Import a registrace blueprintů
    from app.views.routes import views
    from app.views.admin_routes import admin
    from app.views.cart_routes import cart
    from app.views.checkout_routes import checkout

    app.register_blueprint(api_cart, url_prefix="/api/cart")
    app.register_blueprint(views)
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(cart)
    app.register_blueprint(checkout)

    # Kontextový procesor – zobrazování počtu v košíku
    @app.context_processor
    def inject_cart_count():
        if current_user.is_authenticated:
            cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
            cart_count = sum(item.quantity for item in cart_items)
        else:
            cart_count = 0
        return dict(cart_item_count=cart_count)

    return app
