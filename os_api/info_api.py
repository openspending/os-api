from flask import Blueprint, current_app
from flask.ext.jsonpify import jsonify

infoAPI = Blueprint('InfoAPI', __name__)


@infoAPI.route('/info/<slug>/package')
def get_package(slug):
    mr = current_app.extensions['model_registry']
    if mr.has_model(slug):
        return jsonify(mr.get_package(slug))
