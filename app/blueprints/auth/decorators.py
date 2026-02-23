from functools import wraps
from flask import abort
from flask_login import current_user


def admin_required(f):
    """Decorator: restricts route to Admin role only."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


def login_and_role_required(role: str):
    """Decorator factory for role-based access; use @login_and_role_required('Admin')."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if role == "Admin" and not current_user.is_admin:
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator
