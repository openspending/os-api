from flask import Flask, jsonify
from flask.ext.cors import CORS

from babbage.api import configure_api
from babbage_fiscal import FDPLoaderBlueprint, ModelRegistry

from cube_manager import OSCubeManager

from config import get_engine

from backward import configure_backward_api

app = Flask('os_api')


def configure_app(app):
    manager = OSCubeManager(get_engine())
    app.register_blueprint(configure_api(app, manager), url_prefix='/api/3')
    app.register_blueprint(FDPLoaderBlueprint, url_prefix='/api/3/loader')
    app.register_blueprint(configure_backward_api(app, manager), url_prefix='/api/2')
    app.extensions['model_registry'] = ModelRegistry(get_engine())
    CORS(app)

configure_app(app)


@app.route('/api/3/<slug>/package')
def get_package(slug):
    mr = app.extensions['model_registry']
    if mr.has_model(slug):
        return jsonify(mr.get_package(slug))

if __name__ == "__main__":
    app.run(port=8000, debug=True)
