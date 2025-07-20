from flask import Blueprint, render_template, session, redirect, url_for, flash

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/dashboard')
def dashboard():
    if not session.get('user_id'):
        flash("Debes iniciar sesión para ver el dashboard", "warning")
        return redirect(url_for('auth.login'))
    return render_template('user/dashboard.html')


@user_bp.route('/profile')
def profile():
    # lógica para mostrar perfil
    return render_template('user/profile.html')

@user_bp.route('/courses')
def courses():
    # lógica para mostrar cursos del usuario
    return render_template('user/courses.html')

@user_bp.route('/settings')
def settings():
    # configuración de usuario
    return render_template('user/settings.html')