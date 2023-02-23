# project/server/config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig(object):
    """Base configuration."""

    WTF_CSRF_ENABLED = True
    REDIS_URL = os.getenv('REDISTOGO_URL')
    QUEUES = ["default"]


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    WTF_CSRF_ENABLED = False
    REDIS_URL = "redis://redis:6379/0"


class TestingConfig(BaseConfig):
    """Testing configuration."""

    TESTING = True
    WTF_CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXEPTION = False
