import json
from flask import request, Response, url_for
from flask_restful import Resource
from sensorhub import cache
from sensorhub.constants import *
from sensorhub.models import Measurement, Sensor
from sensorhub.utils import page_key, require_sensor_key


class MeasurementItem(Resource):

    def get(self, sensor, measurement):
        pass


class MeasurementCollection(Resource):

    @cache.cached(timeout=None, make_cache_key=page_key, response_filter=lambda r: False)
    def get(self, sensor):
        db_sensor = Sensor.query.filter_by(name=sensor).first()
        if db_sensor is None:
            raise NotFound
        page = request.args.get("page", 0)
        remaining = Measurement.query.filter_by(
            sensor=db_sensor
        ).order_by("time").offset(page * self.PAGE_SIZE)
        body = {
            "sensor": db_sensor.name,
            "measurements": []
        }
        for meas in remaining.limit(self.PAGE_SIZE):
            body["measurements"].append(
                {
                    "value": meas.value,
                    "time": meas.time.isoformat()
                }
            )
        response = Response(json.dumps(body), 200, mimetype=JSON)
        if len(body["measurements"]) == self.PAGE_SIZE:
            cache.set(page_key(), response, timeout=None)
        return response

    @require_sensor_key
    def post(self, sensor):
        return Response(501)
        
