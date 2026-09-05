from functools import wraps

from flask import (
    flash,
    redirect,
    session,
    url_for
)


def login_required(view):

    @wraps(view)
    def wrapped_view(*args, **kwargs):

        if "usuario_id" not in session:
            flash("Faça login para continuar.", "warning")
            return redirect(url_for("auth.login"))

        return view(*args, **kwargs)

    return wrapped_view