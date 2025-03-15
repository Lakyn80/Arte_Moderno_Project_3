import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO

# Zaregistrování fontu s diakritikou
font_path = os.path.join(os.path.dirname(__file__), 'static', 'fonts', 'DejaVuSans.ttf')
pdfmetrics.registerFont(TTFont("DejaVu", font_path))

def generate_invoice_pdf(order):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("DejaVu", 16)
    c.drawString(50, height - 50, f"Faktura – Objednávka č. {order.order_number}")

    c.setFont("DejaVu", 12)
    y = height - 100
    c.drawString(50, y, f"Zákazník: {order.user.first_name or ''} {order.user.last_name or ''}")
    y -= 20
    c.drawString(50, y, f"E-mail: {order.user.email}")
    y -= 20
    if order.address:
        c.drawString(50, y, f"Dodací adresa: {order.address}")
        y -= 20
    if order.billing_address:
        c.drawString(50, y, f"Fakturační adresa: {order.billing_address}")
        y -= 20

    y -= 20
    c.drawString(50, y, "Seznam položek:")
    y -= 20

    for item in order.items:
        item_line = f"{item.product.name} – {item.quantity} ks × {item.price_per_item:.2f} Kč = {item.quantity * item.price_per_item:.2f} Kč"
        c.drawString(60, y, item_line)
        y -= 20
        if y < 100:
            c.showPage()
            c.setFont("DejaVu", 12)
            y = height - 100

    y -= 10
    c.setFont("DejaVu", 12)
    c.drawString(50, y, f"Celková cena: {order.total_price:.2f} Kč")

    c.save()
    buffer.seek(0)
    return buffer
