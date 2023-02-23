# project/server/__init__.py
from .main.models import User
import os

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin


# instantiate the extensions
bootstrap = Bootstrap()
login_manager = LoginManager()
# login_manager.login_view = 'login'
login_manager.login_view = 'auth.login'


def create_app(script_info=None):
    print('in the create_app function')

    # instantiate the app
    app = Flask(
        __name__,
        template_folder="../client/templates",
        static_folder="../client/static",
    )

    app.config['SECRET_KEY'] = '98ayh13uab9n902'
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    app.secret_key = 'key'

    login_manager.init_app(app)

    # set config
    app_settings = os.getenv("APP_SETTINGS")

    app.config.from_object(app_settings)

    # set up extensions
    bootstrap.init_app(app)

    # register blueprints
    from project.server.main.views import bp as view_bp

    app.register_blueprint(view_bp)

    from project.server.main.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    # shell context for flask cli
    app.shell_context_processor({"app": app})

    return app


users = {'test_user': {'pw': 'test_password'}
         }


@login_manager.user_loader
def user_loader(username):
    if username not in users:
        return
    user = User()
    user.id = username
    return user


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    if username not in users:
        return

    user = User()
    user.id = username

    user.is_authenticated = request.form['pw'] == users[username]['pw']
    return user
