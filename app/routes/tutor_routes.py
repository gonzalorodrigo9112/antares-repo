# from flask import Blueprint, render_template, request, redirect, url_for, session, flash
# import os
# from werkzeug.utils import secure_filename
# from ddbb.connection.conector import get_mysql_connection

# tutor_bp = Blueprint('tutor', __name__)

# UPLOAD_FOLDER = 'uploads'

# # ==============================
# # Ruta: Crear un nuevo curso
# # ==============================
# @tutor_bp.route('/create_course', methods=['GET', 'POST'])
# def create_course():
#     if session.get('user_role') != 'tutor':
#         flash("Solo los tutores pueden acceder a esta sección", "error")
#         return redirect(url_for('public.home'))

#     if request.method == 'POST':
#         title = request.form['title']
#         description = request.form['description']

#         # Crear curso en la base de datos
#         connection = get_mysql_connection()
#         cursor = connection.cursor()

#         cursor.callproc('sp_create_course', (title, description, session['user_id'], 'pendiente'))
#         connection.commit()

#         # Obtener el ID del curso recién creado
#         cursor.execute("SELECT LAST_INSERT_ID()")
#         course_id = cursor.fetchone()[0]

#         # Crear carpeta física para almacenar archivos
#         folder_path = os.path.join(UPLOAD_FOLDER, f"course_{course_id}")
#         os.makedirs(folder_path, exist_ok=True)

#         flash("Curso creado correctamente. Esperando aprobación del administrador.", "success")
#         return redirect(url_for('tutor.upload_materials', course_id=course_id))

#     return render_template('tutor/create_course.html')


# # =============================================
# # Ruta: Subir materiales (solo después de crear)
# # =============================================
# @tutor_bp.route('/upload_materials/<int:course_id>', methods=['GET', 'POST'])
# def upload_materials(course_id):
#     if session.get('user_role') != 'tutor':
#         flash("Acceso denegado. Solo tutores pueden subir materiales.", "error")
#         return redirect(url_for('public.home'))

#     folder_path = os.path.join(UPLOAD_FOLDER, f"course_{course_id}")

#     if request.method == 'POST':
#         files = request.files.getlist('materials')

#         for file in files:
#             if file and file.filename:
#                 filename = secure_filename(file.filename)
#                 file.save(os.path.join(folder_path, filename))
#                 # Podés agregar lógica para insertar info en una tabla "materials" si querés

#         flash("Materiales subidos correctamente.", "success")
#         return redirect(url_for('tutor.upload_materials', course_id=course_id))

#     return render_template('tutor/upload_materials.html', course_id=course_id)




#//////////////////////////////////////////////////////////////7
# tutor_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from ddbb.connection.conector import get_mysql_connection

tutor_bp = Blueprint('tutor', __name__, template_folder='../templates/tutor')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'mp4', 'mov', 'avi'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @tutor_bp.route('/upload_materials/<int:course_id>', methods=['GET', 'POST'])
# def upload_materials(course_id):
#     if 'user_id' not in session or session.get('role') != 'tutor':
#         flash('Acceso denegado. Inicia sesión como tutor.', 'danger')
#         return redirect(url_for('auth.login'))

#     tutor_id = session['user_id']

#     # Validar que el curso pertenezca al tutor actual y que esté aprobado
#     conn = get_mysql_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("""
#         SELECT id, title, is_approved 
#         FROM courses 
#         WHERE id = %s AND tutor_id = %s
#     """, (course_id, tutor_id))
#     curso = cursor.fetchone()

#     if not curso:
#         flash("No tienes permiso para gestionar este curso.", "danger")
#         return redirect(url_for('tutor.dashboard'))

#     if not curso['is_approved']:
#         flash("Este curso aún no fue aprobado por un administrador.", "warning")
#         return redirect(url_for('tutor.dashboard'))

#     if request.method == 'POST':
#         file = request.files.get('file')
#         file_type = request.form.get('file_type')

#         if not file or not allowed_file(file.filename):
#             flash('Archivo inválido o tipo no permitido.', 'danger')
#             return redirect(request.url)

#         filename = secure_filename(file.filename)
#         course_folder = os.path.join(UPLOAD_FOLDER, f'course_{course_id}')

#         os.makedirs(course_folder, exist_ok=True)
#         file_path = os.path.join(course_folder, filename)
#         file.save(file_path)

#         # Guardar en base de datos
#         rel_path = os.path.relpath(file_path)  # guardar ruta relativa
#         now = datetime.now()

#         cursor.execute("""
#             INSERT INTO materials (course_id, file_type, file_path, uploaded_at)
#             VALUES (%s, %s, %s, %s)
#         """, (course_id, file_type, rel_path, now))
#         conn.commit()

#         flash('Archivo subido correctamente.', 'success')
#         return redirect(url_for('tutor.upload_materials', course_id=course_id))

#     # Cargar materiales existentes
#     cursor.execute("""
#         SELECT id, file_type, file_path, uploaded_at 
#         FROM materials 
#         WHERE course_id = %s
#         ORDER BY uploaded_at DESC
#     """, (course_id,))
#     materials = cursor.fetchall()

#     conn.close()

#     return render_template('tutor/upload_materials.html', course_id=course_id, materials=materials)

#--------------------- upload_materials NUEVO ---------------------
@tutor_bp.route('/upload_materials/<int:course_id>', methods=['GET', 'POST'])
def upload_materials(course_id):
    if session.get('user_role') != 'tutor':
        flash("Solo los tutores pueden subir materiales", "error")
        return redirect(url_for('public.home'))

    connection = get_mysql_connection()
    cursor = connection.cursor(dictionary=True)

    # Verificar que el curso exista y pertenezca al tutor actual
    cursor.execute("SELECT * FROM courses WHERE id = %s AND tutor_id = %s", (course_id, session['user_id']))
    course = cursor.fetchone()

    if not course:
        flash("Curso no encontrado o no autorizado.", "error")
        return redirect(url_for('tutor.create_course'))

    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        material_type = request.form.get('type')  # video, image, pdf, etc.

        if not uploaded_file:
            flash("No se seleccionó ningún archivo.", "error")
            return redirect(request.url)

        filename = secure_filename(uploaded_file.filename)

        # Validación por tipo
        allowed_extensions = {
            'video': ['.mp4', '.mov', '.avi'],
            'image': ['.jpg', '.jpeg', '.png'],
            'pdf': ['.pdf'],
        }

        ext = os.path.splitext(filename)[1].lower()

        if ext not in allowed_extensions.get(material_type, []):
            flash("Tipo de archivo no permitido para este material.", "error")
            return redirect(request.url)

        # Guardar archivo
        folder_path = os.path.join('uploads', f"course_{course_id}")
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, filename)
        uploaded_file.save(file_path)

        # Registrar en la base de datos
        cursor.execute("""
            INSERT INTO materials (course_id, file_name, file_path, file_type)
            VALUES (%s, %s, %s, %s)
        """, (course_id, filename, file_path, material_type))

        connection.commit()
        flash("Archivo subido correctamente.", "success")
        return redirect(request.url)

    return render_template('tutor/upload_materials.html', course=course)

#-------------------------------------
from flask import send_from_directory, abort

# Ruta para listar materiales visibles según rol
@tutor_bp.route('/materials/<int:course_id>')
def list_materials(course_id):
    user_id = session.get('user_id')
    role = session.get('user_role')

    connection = get_mysql_connection()
    cursor = connection.cursor(dictionary=True)

    # 🔒 Control de acceso por rol
    if role == 'tutor':
        cursor.execute("SELECT * FROM courses WHERE id = %s AND tutor_id = %s", (course_id, user_id))
        course = cursor.fetchone()
        if not course:
            flash("No autorizado para ver los materiales de este curso.", "error")
            return redirect(url_for('public.home'))

    elif role == 'student':
        # Validar si el estudiante compró el curso
        cursor.execute("""
            SELECT * FROM student_courses WHERE student_id = %s AND course_id = %s
        """, (user_id, course_id))
        access = cursor.fetchone()
        if not access:
            flash("Debes comprar el curso para acceder a sus materiales.", "error")
            return redirect(url_for('public.home'))

    elif role == 'admin':
        pass  # acceso total

    else:
        flash("Iniciá sesión para ver materiales.", "error")
        return redirect(url_for('auth.login'))

    # ✅ Obtener materiales
    cursor.execute("SELECT * FROM materials WHERE course_id = %s", (course_id,))
    materials = cursor.fetchall()

    return render_template('materials/list.html', materials=materials, course_id=course_id)



#------------------------------------------------

@tutor_bp.route('/download_material/<int:course_id>/<filename>')
def download_material(course_id, filename):
    user_id = session.get('user_id')
    role = session.get('user_role')

    # Verificar acceso como en la vista anterior
    connection = get_mysql_connection()
    cursor = connection.cursor(dictionary=True)

    access_granted = False

    if role == 'tutor':
        cursor.execute("SELECT * FROM courses WHERE id = %s AND tutor_id = %s", (course_id, user_id))
        if cursor.fetchone():
            access_granted = True

    elif role == 'student':
        cursor.execute("SELECT * FROM student_courses WHERE student_id = %s AND course_id = %s", (user_id, course_id))
        if cursor.fetchone():
            access_granted = True

    elif role == 'admin':
        access_granted = True

    if not access_granted:
        flash("No autorizado.", "error")
        return redirect(url_for('public.home'))

    folder = os.path.join('uploads', f'course_{course_id}')
    return send_from_directory(folder, filename, as_attachment=True)
