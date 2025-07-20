# app/routes/auth_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from ddbb.connection.conector import get_mysql_connection
from firebase.firebase_init import get_firebase_db
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
import bcrypt

auth_bp = Blueprint('auth', __name__)

# --------------------- UTILS ---------------------

def generate_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

def send_reset_email(to_email, reset_url):
    msg = Message(subject="Recuperación de contraseña - Antares",
                  sender=("Antares", current_app.config['MAIL_USERNAME']),
                  recipients=[to_email])
    msg.body = f"""Hola,

Has solicitado restablecer tu contraseña.

Haz clic en el siguiente enlace para crear una nueva contraseña:
{reset_url}

Este enlace expirará en 1 hora.

Si no lo solicitaste, simplemente ignora este correo.
"""
    from app import mail  # importante si usás Flask-Mail
    mail.send(msg)

# --------------------- REGISTER ---------------------

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    error = None

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('rol', '').strip()

        if not all([username, full_name, email, password, role]):
            error = "Por favor, completá todos los campos obligatorios."
            flash("Todos los campos son obligatorios", "danger")
            return render_template('auth/register.html', error=error)

        try:
            conn = get_mysql_connection()
            cursor = conn.cursor(dictionary=True)

            # Verificación de duplicados
            cursor.execute("SELECT id FROM users WHERE email = %s OR username = %s", (email, username))
            if cursor.fetchone():
                flash("El correo o el nombre de usuario ya están registrados", "warning")
                return render_template('auth/register.html')

            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            query = "INSERT INTO users (full_name, username, email, password_hash, role) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (full_name, username, email, hashed_pw, role))
            user_id = cursor.lastrowid

            # Firebase
            ref = get_firebase_db().reference(f"users/{user_id}")
            ref.set({
                "full_name": full_name,
                "email": email,
                "role": role
            })

            conn.commit()
            flash("Registro exitoso. Inicia sesión.", "success")
            return redirect(url_for('auth.login'))

        except Exception as e:
            print(f"[ERROR] {e}")
            error = "Error en el registro"
            flash(error, "danger")
            return render_template('auth/register.html', error=error)

        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    return render_template('auth/register.html', error=error)
# --------------------- LOGIN ---------------------

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_input = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not user_input or not password:
            flash("Completa todos los campos", "danger")
            return render_template('auth/login.html')

        try:
            conn = get_mysql_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM users WHERE email = %s OR full_name = %s", (user_input, user_input))
            user = cursor.fetchone()

            if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                session['user_id'] = user['id']
                session['user_name'] = user['full_name']
                session['user_role'] = user['role']
                flash(f"Bienvenido, {user['full_name']}", "success")
                return redirect(url_for('public.home'))  # Asegurate de tener esta vista
            else:
                flash("Credenciales inválidas", "danger")

        except Exception as e:
            print(f"[ERROR LOGIN] {e}")
            flash("Error al iniciar sesión", "danger")

        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    return render_template('auth/login.html')

# --------------------- FORGOT PASSWORD ---------------------

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()

        if not email:
            flash("Por favor ingresa tu correo electrónico", "warning")
            return render_template('auth/forgot_password.html')

        try:
            conn = get_mysql_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user:
                serializer = generate_serializer()
                token = serializer.dumps(email, salt='password-reset-salt')
                reset_url = url_for('auth.reset_password', token=token, _external=True)
                send_reset_email(email, reset_url)
                flash("Te hemos enviado un correo con el enlace de recuperación.", "info")
            else:
                flash("Ese correo no está registrado.", "danger")

        except Exception as e:
            print(f"[ERROR FORGOT PASSWORD] {e}")
            flash("Ocurrió un error procesando tu solicitud.", "danger")

        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    return render_template('auth/forgot_password.html')

# --------------------- RESET PASSWORD ---------------------

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    serializer = generate_serializer()
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)

        if request.method == 'POST':
            new_password = request.form.get('password', '').strip()

            if not new_password:
                flash("La nueva contraseña no puede estar vacía", "warning")
                return render_template('auth/reset_password.html')

            hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

            try:
                conn = get_mysql_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET password_hash = %s WHERE email = %s", (hashed_pw, email))
                conn.commit()
                flash("Contraseña actualizada correctamente. Ahora podés iniciar sesión.", "success")
                return redirect(url_for('auth.login'))

            except Exception as e:
                print(f"[ERROR RESET PASSWORD] {e}")
                flash("Ocurrió un error actualizando la contraseña.", "danger")

            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

        return render_template('auth/reset_password.html')

    except Exception as e:
        print(f"[TOKEN ERROR] {e}")
        flash("El enlace de recuperación ha expirado o es inválido.", "danger")
        return redirect(url_for('auth.forgot_password'))



@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for('public.home'))
