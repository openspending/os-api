import sys
import os
import logging

from flask import Flask
from flask.ext.cors import CORS
from werkzeug.contrib.fixers import ProxyFix

from raven.contrib.flask import Sentry

from babbage.api import configure_api as configure_babbage_api
from os_package_registry import PackageRegistry

from .config import get_engine

from .cube_manager import OSCubeManager
from .info_api import infoAPI

from .cache import setup_caching
from .stats import setup_stats

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path)


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

    registry = PackageRegistry(
        es_connection_string=os.environ.get('OS_ELASTICSEARCH_ADDRESS',
                                            'localhost:9200'))
    manager = OSCubeManager(get_engine(), registry)

    logging.info('OS-API configuring query blueprints')
    _app.register_blueprint(configure_babbage_api(_app, manager),
                            url_prefix='/api/3')
    _app.register_blueprint(infoAPI, url_prefix='/api/3')

    _app.extensions['model_registry'] = registry

    CORS(_app)
    Sentry(_app, dsn=os.environ.get('SENTRY_DSN', ''))

    logging.info('OS-API app created')
    return _app


setup_logging()

app = create_app()

setup_caching(app)
setup_stats(app)
