import os
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from flask import Flask, request, url_for
from flask.ext.cors import CORS

from babbage.api import configure_api as configure_babbage_api
from babbage_fiscal import configure_loader_api, ModelRegistry

from .cube_manager import OSCubeManager

from .config import get_engine, _connection_string

from .backward import configure_backward_api
from .info_api import infoAPI


def create_app():
    app = Flask('os_api')
    manager = OSCubeManager(get_engine())
    app.register_blueprint(configure_babbage_api(app, manager), url_prefix='/api/3')
    app.register_blueprint(configure_loader_api(_connection_string), url_prefix='/api/3/loader')
    app.register_blueprint(configure_backward_api(app, manager), url_prefix='/api/2')
    app.register_blueprint(infoAPI, url_prefix='/api/3')
    app.extensions['model_registry'] = ModelRegistry(get_engine())
    CORS(app)
    return app


app = create_app()

cache = None
cache_timeout = None
if 'OS_API_CACHE' in os.environ:
    from werkzeug.contrib.cache import MemcachedCache
    cache = MemcachedCache([os.environ['OS_API_CACHE']])
    cache_timeout = int(os.environ.get('OS_API_CACHE_TIMEOUT',3600))


@app.before_request
def return_cached():
    o = urlparse(request.url)
    if cache is not None \
            and not o.path.startswith(url_for('FDPLoader.load'))\
            and not o.path.startswith(url_for('babbage_api.cubes')):
        key = o.path+'?'+o.query
        response = cache.get(key)
        if response:
            response.from_cache = True
            return response


@app.after_request
def cache_response(response):
    o = urlparse(request.url)
    if cache is not None and response.status_code == 200 and not hasattr(response, 'from_cache'):
        key = o.path+'?'+o.query
        cache.set(key, response, cache_timeout)
    return response
