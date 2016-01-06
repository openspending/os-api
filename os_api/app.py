from flask import Flask
from flask.ext.cors import CORS

from babbage.api import configure_api as configure_babbage_api
from babbage_fiscal import FDPLoaderBlueprint, ModelRegistry

from .cube_manager import OSCubeManager

from .config import get_engine

from .backward import configure_backward_api
from .info_api import infoAPI


def create_app():
    app = Flask('os_api')
    manager = OSCubeManager(get_engine())
    app.register_blueprint(configure_babbage_api(app, manager), url_prefix='/api/3')
    app.register_blueprint(FDPLoaderBlueprint, url_prefix='/api/3/loader')
    app.register_blueprint(configure_backward_api(app, manager), url_prefix='/api/2')
    app.register_blueprint(infoAPI, url_prefix='/api/3')
    app.extensions['model_registry'] = ModelRegistry(get_engine())
    CORS(app)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=8000, debug=True)
