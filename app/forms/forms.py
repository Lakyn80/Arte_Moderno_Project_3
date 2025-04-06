from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import Optional, DataRequired, Email, EqualTo, Length, ValidationError
from datetime import datetime

def validate_past_date(form, field):
    if not field.data:
        return
    try:
        date_value = datetime.strptime(field.data, "%Y-%m-%d")
        if date_value > datetime.today():
            raise ValidationError("Datum narození nemůže být v budoucnosti.")
    except ValueError:
        raise ValidationError("Neplatný formát data (očekáváno: RRRR-MM-DD).")

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
    date_of_birth = StringField("Datum narození", validators=[Optional(), validate_past_date])
    submit = SubmitField("Uložit profil")

class ClientResetRequestForm(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    submit = SubmitField("Odeslat odkaz pro obnovu hesla")

class ClientResetPasswordForm(FlaskForm):
    new_password = PasswordField("Nové heslo", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Potvrdit nové heslo", validators=[DataRequired(), EqualTo("new_password")])
    submit = SubmitField("Změnit heslo")

class ContactForm(FlaskForm):
    name = StringField("Jméno", validators=[DataRequired()])
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    subject = StringField("Předmět", validators=[Optional()])
    message = TextAreaField("Zpráva", validators=[DataRequired()])
    submit = SubmitField("Odeslat")
