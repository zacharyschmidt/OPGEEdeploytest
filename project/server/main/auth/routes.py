
from flask_login import login_user
from flask_login import UserMixin
from flask import render_template, Blueprint, jsonify, request, current_app, redirect, url_for
from ..models import User
from project.server.main.auth import bp
from project.server import users

@bp.route("/", methods=['GET', 'POST'])
def login():
    print('login')
    if request.method == 'POST':
        username = request.form.get('username')
        if request.form.get('pw') == users[username]['pw']:
            user = User()
            user.id = username
            login_user(user)
            return redirect(url_for('views.private'))
    return render_template('login/login.html')
