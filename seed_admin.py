from app import db, create_app
from app.models import User
from flask_bcrypt import Bcrypt

app = create_app()
bcrypt = Bcrypt(app)

with app.app_context():
    # Zkontroluj, jestli už admin neexistuje
    existing_admin = User.query.filter_by(username='admin').first()
    if not existing_admin:
        hashed_password = bcrypt.generate_password_hash("admin").decode('utf-8')
        admin = User(
            username='admin',
            email='admin@admin.com',
            password=hashed_password,
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin úspěšně vytvořen.")
    else:
        print("⚠️ Admin už existuje.")
