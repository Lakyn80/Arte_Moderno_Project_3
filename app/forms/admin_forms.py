from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class AdminLoginForm(FlaskForm):
    email = StringField("Email", validators=[
        DataRequired(message="Zadejte e-mail."),
        Email(message="Zadejte platný e-mail."),
        Length(max=120)
    ])
    password = PasswordField("Heslo", validators=[
        DataRequired(message="Zadejte heslo."),
        Length(min=6, message="Heslo musí mít alespoň 6 znaků.")
    ])
    submit = SubmitField("Přihlásit")

class AdminChangePasswordForm(FlaskForm):
    old_password = PasswordField("Staré heslo", validators=[
        DataRequired(message="Zadejte staré heslo.")
    ])
    new_password = PasswordField("Nové heslo", validators=[
        DataRequired(message="Zadejte nové heslo."),
        Length(min=6, message="Nové heslo musí mít alespoň 6 znaků.")
    ])
    confirm_password = PasswordField("Potvrzení nového hesla", validators=[
        DataRequired(message="Zadejte potvrzení nového hesla."),
        EqualTo("new_password", message="Hesla se musí shodovat.")
    ])
    submit = SubmitField("Změnit heslo")
