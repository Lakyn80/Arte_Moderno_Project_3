# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SubmitField
from wtforms.validators import Optional

class ProfileForm(FlaskForm):
    first_name = StringField("Jméno", validators=[Optional()])
    last_name = StringField("Příjmení", validators=[Optional()])
    phone = StringField("Telefon", validators=[Optional()])
    address = TextAreaField("Dodací adresa", validators=[Optional()])
    billing_address = TextAreaField("Fakturační adresa", validators=[Optional()])
    city = StringField("Město", validators=[Optional()])
    postal_code = StringField("PSČ", validators=[Optional()])
    country = StringField("Země", validators=[Optional()])
    company = StringField("Firma", validators=[Optional()])
    company_id = StringField("IČO", validators=[Optional()])
    vat_id = StringField("DIČ", validators=[Optional()])
    note = TextAreaField("Poznámka", validators=[Optional()])
    date_of_birth = DateField("Datum narození", format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField("Uložit profil")
