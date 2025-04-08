from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.forms.forms import ProfileForm

profile = Blueprint("profile", __name__)

@profile.route("/profile", methods=["GET", "POST"])
@login_required
def profil():
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        for field in form:
            if hasattr(current_user, field.name):
                setattr(current_user, field.name, field.data)
        db.session.commit()
        flash("✅ Profil byl úspěšně uložen.", "success")
        return redirect(url_for("profile.profil"))

    return render_template(
        "client/profil.html",
        form=form,
        birthdate=current_user.date_of_birth,
        datetime=datetime
    )
