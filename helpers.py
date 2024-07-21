import re
from flask import redirect, url_for, request, flash, session, render_template
from functools import wraps


def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            flash("Login required", "info")
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

"""Redirect (For redirecting and error) to a page and show messages"""
def red_err(page: str, flash_msg: str = None,  err_msg: str = None):
    if flash_msg:
        flash(flash_msg, "danger")
    if err_msg:
        return render_template("errored.html", err_msg=err_msg)
    return redirect(url_for(page))

def red_scs(page: str, flash_msg: str = None):
    if flash_msg:
        flash(flash_msg, "success")
    return redirect(url_for(page))

"""Function to Retrieve username and password entered in a form"""
def get_nm_pswd():

    form_name = request.form.get("username")
    form_password = request.form.get("password")
    return form_name, form_password


def quote_identifier(identifier):
    """Quote an identifier if it contains special characters."""
    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
        return identifier  # No special characters, return as is
    else:
        return f'"{identifier}"'  # Quote the identifier





