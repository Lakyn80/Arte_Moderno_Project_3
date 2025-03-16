import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.lib import colors
from io import BytesIO

# Zaregistrování fontu s diakritikou
font_path = os.path.join(os.path.dirname(__file__), 'static', 'fonts', 'DejaVuSans.ttf')
pdfmetrics.registerFont(TTFont("DejaVu", font_path))


def generate_invoice_pdf(order):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 30
    y = height - margin

    # Hlavička
    c.setFont("DejaVu", 16)
    c.drawString(margin, y, f"Faktura č. {order.invoice_number}")
    y -= 30

    # Údaje o zákazníkovi
    c.setFont("DejaVu", 12)
    c.drawString(margin, y, "Údaje o zákazníkovi:")
    y -= 20
    c.drawString(margin, y, f"Jméno: {order.user.first_name or ''} {order.user.last_name or ''}")
    y -= 20
    c.drawString(margin, y, f"E-mail: {order.user.email}")
    if order.user.company:
        y -= 20
        c.drawString(margin, y, f"Firma: {order.user.company}")
    if order.user.company_id:
        y -= 20
        c.drawString(margin, y, f"IČO: {order.user.company_id}")
    if order.user.vat_id:
        y -= 20
        c.drawString(margin, y, f"DIČ: {order.user.vat_id}")

    # Adresy
    y -= 30
    c.drawString(margin, y, "Doručovací adresa:")
    y -= 20
    c.drawString(margin, y, order.address or "-")

    if order.billing_address:
        y -= 30
        c.drawString(margin, y, "Fakturační adresa:")
        y -= 20
        c.drawString(margin, y, order.billing_address)

    # Položky objednávky
    y -= 40
    c.setFont("DejaVu", 12)
    c.drawString(margin, y, "Položky objednávky:")
    y -= 25

    # Hlavička tabulky
    c.setFont("DejaVu", 11)
    c.drawString(margin, y, "Produkt")
    c.drawRightString(margin + 220, y, "Množství")
    c.drawRightString(margin + 310, y, "Cena/ks")
    c.drawRightString(margin + 400, y, "Celkem")
    y -= 10
    c.setLineWidth(0.5)
    c.line(margin, y, width - margin, y)
    y -= 15

    # Výpis položek
    for item in order.items:
        c.drawString(margin, y, item.product.name)
        c.drawRightString(margin + 220, y, f"{item.quantity} ks")
        c.drawRightString(margin + 310, y, f"{item.price_per_item:.2f} Kč")
        c.drawRightString(margin + 400, y, f"{item.quantity * item.price_per_item:.2f} Kč")
        y -= 20

        if y < 80:
            c.showPage()
            c.setFont("DejaVu", 11)
            y = height - margin

    # Oddělovač a celková částka
    y -= 10
    c.line(margin, y, width - margin, y)
    y -= 25
    c.setFont("DejaVu", 12)
    c.drawString(margin, y, f"Celková částka k úhradě: {order.total_price:.2f} Kč")
    
    # Poděkování
    y -= 40
    c.setFont("DejaVu", 10)
    c.drawString(margin, y, "Děkujeme za vaši objednávku – Arte Moderno")

    c.save()
    buffer.seek(0)
    return buffer
