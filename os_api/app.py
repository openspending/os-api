from flask import Flask

from babbage.api import configure_api
from babbage_fiscal import FDPLoaderBlueprint

from cube_manager import OSCubeManager

from config import get_engine

app = Flask('os_api')

manager = OSCubeManager(get_engine())
blueprint = configure_api(app, manager)
app.register_blueprint(blueprint, url_prefix='/api/3')
app.register_blueprint(FDPLoaderBlueprint, url_prefix='/api/3/loader')

if __name__ == "__main__":
    app.run(port=8000)
