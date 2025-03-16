# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SubmitField
from wtforms.validators import Optional

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

# 📧 Formulář pro žádost o reset hesla – klient
class ClientResetRequestForm(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    submit = SubmitField("Odeslat odkaz pro obnovu hesla")

# 🔑 Formulář pro nové heslo – klient
class ClientResetPasswordForm(FlaskForm):
    new_password = PasswordField("Nové heslo", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Potvrdit nové heslo", validators=[DataRequired(), EqualTo("new_password")])
    submit = SubmitField("Změnit heslo")


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
