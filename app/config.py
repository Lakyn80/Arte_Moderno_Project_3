import os
from dotenv import load_dotenv

# Načte proměnné z .env při lokálním spuštění
load_dotenv()

class Config:
    # Bezpečnostní klíče
    SECRET_KEY = os.getenv('SECRET_KEY', 'arte_moderno')
    WTF_CSRF_SECRET_KEY = os.getenv('WTF_CSRF_SECRET_KEY', 'c0ea893fc51c8912e8f18bbde18cbdd78fe05014f70a2dd94a775a7ed05eb2ce')
    WTF_CSRF_ENABLED = True

    # Databáze – použije PostgreSQL z Renderu, jinak SQLite pro vývoj
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')               
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploady
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # Admin přihlašovací údaje (můžeš změnit i přes Render Environment Variables)
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'arte2024')

    # Konfigurace Flask-Mail
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'artemodernoblaha@gmail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'qxunfbtnyvefainm')
