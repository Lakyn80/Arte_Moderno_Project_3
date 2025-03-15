# ---------- Order number----------
from datetime import datetime
import random

def generate_order_number():
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = str(random.randint(1000, 9999))
    return f"OBJ-{date_part}-{random_part}"
