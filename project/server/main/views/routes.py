# project/server/main/views.py

import redis
from rq import Queue, Connection
from rq.registry import StartedJobRegistry, DeferredJobRegistry
from flask import render_template, Blueprint, jsonify, request, current_app, redirect, url_for, abort, send_from_directory

import flask_login as flask_login
from flask_login import LoginManager, UserMixin

from project.server.main.views import bp
from project.server.main.tasks import get_data
import time
import os


def send_file():
    try:

        return send_from_directory(
            '/usr/src/app', filename='test_rmi.csv', as_attachment=True)
    except FileNotFoundError:
        abort(404)


@bp.route("/private", methods=['GET', 'POST'])
@flask_login.login_required
def private():
    return render_template("main/home.html")

@bp.route("/tasks", methods=['POST'])
def run_task():
    # task_type = request.form["type"]

    with Connection(redis.from_url(current_app.config['REDIS_URL'])):
        try:
            # make a task that prints current directory
            q = Queue()
            task1 = q.enqueue(get_data, job_id='get_data')
      
        except (RuntimeError, TypeError, NameError):
            abort(401)

    response_object = {
        "status": "success",
        "data": {
            "task_id": task1.get_id()
        }
    }

    return jsonify(response_object), 202


@bp.route("/download", methods=['GET', 'POST'])
def download():
    print(os.getcwd())
    return send_from_directory(
        '/usr/src/app', filename='opgee_output.xlsx', as_attachment=True)


@bp.route("/tasks/<task_id>", methods=['GET'])
def get_status(task_id):
    with Connection(redis.from_url(current_app.config['REDIS_URL'])):
        q = Queue()
        task = q.fetch_job(task_id)
   
    if task:
        response_object = {
            "status": "success",
            "data": {
                "task_id": task.get_id(),
                "task_status": task.get_status(),
                # "task_result": task.result[0],
            },
        }
        if task.get_status() == 'finished':
            result_df = task.result
            result_df.to_excel('opgee_output.xlsx')
    else:
        response_object = {"status": "error"}
    return jsonify(response_object)
