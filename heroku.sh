#!/bin/bash
gunicorn "project.server:create_app()" --daemon
python3 manage.py run_worker