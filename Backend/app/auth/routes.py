from . import auth_bp


@auth_bp.route('/login')
def login():
    return "Login Page"

@auth_bp.route('/logout')
def logout():
    return "Logout Page"

