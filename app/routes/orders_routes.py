from flask import Blueprint, render_template, redirect, url_for, flash, send_file, session
from flask_login import login_required, current_user
from flask_mail import Message
from pytz import timezone, UTC
from datetime import datetime
from app import mail
from app.models import Order
from app.pdf_generator import generate_invoice_pdf

orders = Blueprint("orders", __name__)

@orders.route("/moje-objednavky")
@login_required
def moje_objednavky():
    orders_list = Order.query.filter_by(user_id=current_user.id, visible_to_user=True)\
                             .order_by(Order.created_at.desc()).all()
    order_data = [
        (order, order.created_at.replace(tzinfo=UTC).astimezone(timezone(order.timezone or 'UTC')))
        for order in orders_list
    ]
    return render_template("client/moje_objednavky.html", order_data=order_data)

@orders.route("/objednavka/<int:order_id>")
@login_required
def detail_objednavky(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id, visible_to_user=True).first()
    if not order:
        flash("Objednávka nenalezena.", "warning")
        return redirect(url_for("orders.moje_objednavky"))

    local_time = order.created_at.replace(tzinfo=UTC).astimezone(timezone(order.timezone or 'UTC'))
    return render_template("client/detail_objednavky.html", order=order, local_time=local_time)

@orders.route("/objednavka/<int:order_id>/faktura")
@login_required
def stahnout_fakturu(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id, visible_to_user=True).first()
    if not order:
        flash("Faktura není dostupná.", "warning")
        return redirect(url_for("orders.moje_objednavky"))

    return send_file(generate_invoice_pdf(order), mimetype="application/pdf", as_attachment=True,
                     download_name=f"faktura_{order.invoice_number}.pdf")

@orders.route("/objednavka/<int:order_id>/faktura/email")
@login_required
def poslat_fakturu_emailem(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id, visible_to_user=True).first()
    if not order:
        flash("Faktura není dostupná.", "warning")
        return redirect(url_for("orders.moje_objednavky"))

    buffer = generate_invoice_pdf(order)

    msg = Message(subject=f"Faktura č. {order.invoice_number}",
                  sender="info@tvujeshop.cz",
                  recipients=[current_user.email])
    msg.body = f"Dobrý den,\n\nPřikládáme fakturu k vaší objednávce č. {order.invoice_number}.\nDěkujeme."
    msg.attach(f"faktura_{order.invoice_number}.pdf", "application/pdf", buffer.read())
    mail.send(msg)

    flash("Faktura byla odeslána.", "success")
    return redirect(url_for("orders.moje_objednavky"))
