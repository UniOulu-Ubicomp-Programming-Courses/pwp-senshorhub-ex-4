import json
from flask import Blueprint, Response
from flask_restful import Api

from sensorhub.resources.sensor import SensorCollection, SensorItem
from sensorhub.resources.location import LocationItem
from sensorhub.resources.measurement import MeasurementCollection

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

api.add_resource(SensorCollection, "/sensors/")
api.add_resource(SensorItem, "/sensors/<sensor:sensor>/")
api.add_resource(LocationItem, "/locations/<location>/")
api.add_resource(MeasurementCollection, "/sensors/<sensor:sensor>/measurements/")

@api_bp.route("/")
def entry():
    return Response(json.dumps({"api_version": "1.0", "api_name": "sensorhub"}), 200)
