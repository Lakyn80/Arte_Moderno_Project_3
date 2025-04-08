from flask import Blueprint, session, request, redirect, url_for

language = Blueprint("language", __name__, url_prefix="/language")

@language.route("/set/<lang_code>")
def set_language(lang_code):
    session['lang'] = lang_code
    print("Nastaven jazyk:", lang_code)
    return redirect(request.referrer or url_for('views.home'))


