from flask import Blueprint, render_template, session, redirect, url_for, flash

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard')
def dashboard():
    if not session.get('user_id') or session.get('user_role') != 'admin':
        flash("Acceso denegado.", "danger")
        return redirect(url_for('auth.login'))
    return render_template('admin/dashboard.html')

@admin_bp.route('/manage_users')
def manage_users():
    # mostrar administración de usuarios
    return render_template('admin/manage_users.html')

@admin_bp.route('/manage_courses')
def manage_courses():
    # mostrar administración de cursos
    return render_template('admin/manage_courses.html')

@admin_bp.route('/reports')
def reports():
    # mostrar reportes y estadísticas
    return render_template('admin/reports.html')