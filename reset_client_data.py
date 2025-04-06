# reset_client_data.py
from app import create_app, db
from app.models import User, Order, OrderItem, CartItem, Inquiry, DiscountCode
from sqlalchemy import delete

app = create_app()

with app.app_context():
    print("🚨 Smažu veškerá klientská data...")

    # SMAZAT OBJEDNÁVKY A POLOŽKY OBJEDNÁVEK
    db.session.execute(delete(OrderItem))
    db.session.execute(delete(Order))

    # SMAZAT POLOŽKY V KOŠÍKU
    db.session.execute(delete(CartItem))

    # SMAZAT DOTAZY Z FORMULÁŘE
    db.session.execute(delete(Inquiry))

    # SMAZAT SLEVOVÉ KÓDY
    db.session.execute(delete(DiscountCode))

    # SMAZAT VŠECHNY KLIENTSKÉ ÚČTY (ne admina)
    deleted_users = User.query.filter(User.is_admin == False).all()
    for user in deleted_users:
        db.session.delete(user)

    db.session.commit()
    print("✅ Všechna klientská data byla smazána.")
