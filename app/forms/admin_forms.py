from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class AdminLoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Heslo", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Přihlásit")

class AdminChangePasswordForm(FlaskForm):
    old_password = PasswordField("Staré heslo", validators=[DataRequired()])
    new_password = PasswordField("Nové heslo", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Potvrzení nového hesla", validators=[
        DataRequired(),
        EqualTo("new_password", message="Hesla se neshodují.")
    ])
    submit = SubmitField("Změnit heslo")

class AdminResetRequestForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Odeslat resetovací odkaz")

class AdminResetPasswordForm(FlaskForm):
    new_password = PasswordField("Nové heslo", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Potvrzení nového hesla", validators=[DataRequired(), EqualTo('new_password', message="Hesla se neshodují")])
    submit = SubmitField("Obnovit heslo")



class AdminUpdateOrderStatusForm(FlaskForm):
    status = SelectField("Stav objednávky", choices=[
        ("nová", "Nová"),
        ("čeká", "Čeká"),
        ("zaplaceno", "Zaplaceno"),
        ("zrušeno", "Zrušeno"),
    ], validators=[DataRequired()])
    submit = SubmitField("Uložit změnu")

from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional

# 📌 Formulář pro změnu stavu objednávky
class AdminUpdateOrderStatusForm(FlaskForm):
    status = SelectField("Změnit stav", choices=[
        ("nová", "Nová"),
        ("čeká", "Čeká"),
        ("zaplaceno", "Zaplaceno"),
        ("zrušeno", "Zrušeno")
    ], validators=[DataRequired()])
    submit = SubmitField("💾 Uložit stav")

# 📝 Formulář pro poznámku k objednávce
class AdminUpdateOrderNoteForm(FlaskForm):
    note = TextAreaField("Poznámka k objednávce", validators=[Optional()])
    submit = SubmitField("💾 Uložit poznámku")
