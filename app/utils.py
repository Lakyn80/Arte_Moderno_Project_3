# ---------- Order number----------
from datetime import datetime
import random
from app.models import Order
from app import db
from sqlalchemy import func

def generate_order_number():
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = str(random.randint(1000, 9999))
    return f"OBJ-{date_part}-{random_part}"



def generate_invoice_number():
    today_str = datetime.utcnow().strftime('%d%m%Y')
    base_number = f"FA-{today_str}"

    # Pokus najít poslední použitou fakturu pro dnešní den
    existing = db.session.query(Order.invoice_number)\
        .filter(Order.invoice_number.like(f"{base_number}-%"))\
        .all()

    existing_numbers = []
    for inv in existing:
        try:
            last_part = inv[0].split("-")[-1]
            existing_numbers.append(int(last_part))
        except:
            continue

    next_number = max(existing_numbers, default=0) + 1
    invoice_number = f"{base_number}-{next_number:02d}"

    return invoice_number
