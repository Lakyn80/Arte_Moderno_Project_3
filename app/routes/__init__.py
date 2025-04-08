from .views_routes import views
from .auth_admin_routes import auth_admin
from .auth_client_routes import auth_client
from .profile_routes import profile
from .cart_routes import cart
from .checkout_routes import checkout
from .orders_routes import orders
from .language_routes import language
from .admin_routes import admin
from .cart_api_routes import api_cart

all_blueprints = [views, auth_admin, auth_client, profile, cart, checkout, orders, language, admin, api_cart,]
