from flask import Flask, render_template
from dotenv import load_dotenv
import os
from flask_mail import Mail
from config import Config
from .routes import main 
# Importá db desde flask_sqlalchemy SOLO UNA VEZ y exportalo en app/extensions.py
# Para evitar conflictos, no definas db aquí y también en extensions.py
from app.extensions import db  # suponiendo que en extensions.py hiciste: db = SQLAlchemy()

# Blueprints
from app.routes.auth_routes import auth_bp
from app.routes.public_routes import public_bp 
from app.routes.user_routes import user_bp
from app.routes.admin_routes import admin_bp

load_dotenv()
mail = Mail()






def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensiones
    db.init_app(app)
    mail.init_app(app)

    # Registrar Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(main)


    # Ruta pública principal
    @app.route('/')
    def public_home():
        return render_template('public.html', fecha_completa="2025 © Antares Academy")

    return app


# Exportar la app
__all__ = ["app"]