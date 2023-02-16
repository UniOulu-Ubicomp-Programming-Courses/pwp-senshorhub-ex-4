import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import UnsupportedMediaType, NotFound, Conflict, BadRequest
from sensorhub.models import Sensor
from sensorhub import db
from sensorhub.utils import require_admin
from sensorhub.constants import *


class SensorCollection(Resource):

    @require_admin
    def get(self):
        body = {"items": []}
        for db_sensor in Sensor.query.all():
            item = db_sensor.serialize(short_form=True)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=JSON)

    def post(self):
        raise NotImplementedError

class SensorItem(Resource):

    def get(self, sensor):
        body = sensor.serialize()
        return Response(json.dumps(body), 200, mimetype=JSON)

    def put(self, sensor):
        if not request.json:
            raise UnsupportedMediaType

        try:
            validate(request.json, Sensor.json_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e))

        sensor.deserialize(request.json)
        try:
            db.session.add(sensor)
            db.session.commit()
        except IntegrityError:
            raise Conflict(
                "Sensor with name '{name}' already exists.".format(
                    **request.json
                )
            )

        return Response(status=204)

    def delete(self, sensor):
        db.session.delete(sensor)
        db.session.commit()

        return Response(status=204)
