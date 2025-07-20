# app/routes.py

from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return "Hola mundo desde el blueprint"
