import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from sensorhub import db
from sensorhub.models import Location, Sensor
from sensorhub.constants import *


class LocationCollection(Resource):

    def get(self):
        raise NotImplementedError


class LocationItem(Resource):

    def get(self, location):
        raise NotImplementedError

