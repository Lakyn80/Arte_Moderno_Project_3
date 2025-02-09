import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'arte_moderno')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///arte_moderno.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # Admin Credentials
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'arte2024')

    # Nastavení pro Flask-Mail
    MAIL_SERVER = 'smtp.gmail.com'  # Gmail SMTP
    MAIL_PORT = 587                 # TLS port
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'artemodernoblaha@gmail.com'  # Váš e-mail
    MAIL_PASSWORD = 'qxunfbtnyvefainm'  # App Password pro Gmail
