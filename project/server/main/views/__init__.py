
from flask import Blueprint

bp = Blueprint('views', __name__)
from project.server.main.views import routes