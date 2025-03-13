from app import db, create_app
from app.models import User
from flask_bcrypt import Bcrypt

# Vytvoření aplikace a bcrypt
app = create_app()
bcrypt = Bcrypt(app)

with app.app_context():
    # Najdeme stávajícího admina podle e-mailu nebo username
    admin = User.query.filter_by(role='admin').first()

    if admin:
        # Nové údaje — můžeš změnit podle potřeby
        new_username = "admin"
        new_email = "lukas.krumpach@gmail.com"
        new_password = "admin2025"

        # Změna dat
        admin.username = new_username
        admin.email = new_email
        admin.password = bcrypt.generate_password_hash(new_password).decode("utf-8")

        db.session.commit()
        print("✅ Admin login údaje byly úspěšně změněny.")
    else:
        print("❌ Admin účet nebyl nalezen.")
