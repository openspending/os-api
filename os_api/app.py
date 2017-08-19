import sys
import os
import logging

from flask import Flask
from flask.ext.cors import CORS
from werkzeug.contrib.fixers import ProxyFix

from raven.contrib.flask import Sentry

from babbage.api import configure_api as configure_babbage_api
from babbage_fiscal import configure_loader_api, ModelRegistry

from .config import get_engine, _connection_string

from .cube_manager import OSCubeManager
from .backward import configure_backward_api
from .info_api import infoAPI

from .cache import setup_caching
from .stats import setup_stats


def setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


def create_app():
    logging.info('OS-API create_app')

    _app = Flask('os_api')
    _app.wsgi_app = ProxyFix(_app.wsgi_app)

    manager = OSCubeManager(get_engine())

    loader = os.environ.get('OS_API_LOADER') is not None

    if loader:
        logging.info('OS-API configuring loader blueprints')
        _app.register_blueprint(configure_loader_api(_connection_string), url_prefix='/api/3/loader')
    else:
        logging.info('OS-API configuring query blueprints')
        _app.register_blueprint(configure_babbage_api(_app, manager), url_prefix='/api/3')
        _app.register_blueprint(configure_backward_api(_app, manager), url_prefix='/api/2')
        _app.register_blueprint(infoAPI, url_prefix='/api/3')

    _app.extensions['model_registry'] = ModelRegistry()
    _app.extensions['loader'] = loader

    CORS(_app)
    # Sentry(_app, dsn=os.environ.get('SENTRY_DSN', ''))

    logging.info('OS-API app created (loader=%s)', loader)
    return _app

setup_logging()

app = create_app()

setup_caching(app)
setup_stats(app)


