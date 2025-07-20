from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from app.routes.auth_routes import auth_bp
from app.ddbb.connection.conector import get_mysql_connection

course_bp = Blueprint('course', __name__, url_prefix='/tutor')

# Directorio base para uploads (configurable en app.config)
UPLOAD_BASE = os.path.join('uploads', 'courses')

ALLOWED_EXTENSIONS = {
    'video': {'mp4', 'mov', 'avi'},
    'image': {'jpg', 'jpeg', 'png', 'gif'},
    'pdf': {'pdf'},
    'texto': {'txt', 'md'}
}

def allowed_file(filename, ftype):
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return ext in ALLOWED_EXTENSIONS.get(ftype, set())

@course_bp.route('/course/new', methods=['GET', 'POST'])
@login_required
def create_course():
    # Solo tutores pueden crear cursos
    if current_user.role != 'tutor':
        flash('No autorizado', 'danger')
        return redirect(url_for('public.home'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        duration = request.form.get('duration')
        # Validaciones básicas omitidas
        # Insertar curso en DB
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO courses (title, description, price, duration, tutor_id) VALUES (%s,%s,%s,%s,%s)",
            (title, description, price, duration, current_user.id)
        )
        course_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        # Crear carpeta física
        path = os.path.join(current_app.root_path, UPLOAD_BASE, str(course_id))
        os.makedirs(path, exist_ok=True)
        flash('Curso creado. Ahora subí materiales.', 'success')
        return redirect(url_for('course.upload_materials', course_id=course_id))

    return render_template('tutor/create_course.html')

@course_bp.route('/course/<int:course_id>/materials', methods=['GET','POST'])
@login_required
def upload_materials(course_id):
    if current_user.role != 'tutor':
        flash('No autorizado', 'danger')
        return redirect(url_for('public.home'))

    if request.method == 'POST':
        ftype = request.form.get('file_type')  # 'video','image','pdf','texto'
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('Seleccioná un archivo', 'warning')
        elif not allowed_file(file.filename, ftype):
            flash('Tipo de archivo no permitido', 'danger')
        else:
            filename = secure_filename(file.filename)
            folder = os.path.join(current_app.root_path, UPLOAD_BASE, str(course_id))
            filepath = os.path.join(folder, filename)
            file.save(filepath)
            # Guardar ruta en DB
            conn = get_mysql_connection()
            cursor = conn.cursor()
            cursor.execute(
                "CALL sp_add_course_file(%s,%s,%s)",
                (course_id, ftype, os.path.join(UPLOAD_BASE, str(course_id), filename))
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash('Material subido con éxito', 'success')

    # Recuperar lista actual de archivos
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("CALL sp_get_course_files(%s)", (course_id,))
    materials = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('tutor/upload_materials.html', course_id=course_id, materials=materials)