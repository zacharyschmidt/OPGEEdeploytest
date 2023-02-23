
from flask import Blueprint

bp = Blueprint('auth', __name__)
from project.server.main.auth import routes