import json
import secrets
from flask import Response, request, url_for
from werkzeug.exceptions import Forbidden, NotFound
from werkzeug.routing import BaseConverter

from sensorhub.constants import *
from sensorhub.models import *

def page_key(*args, **kwargs):
    start = request.args.get("start", 0)
    return request.path + f"[start_{start}]"
    
def require_admin(func):
    def wrapper(*args, **kwargs):
        key_hash = ApiKey.key_hash(request.headers.get("Sensorhub-Api-Key", "").strip())
        db_key = ApiKey.query.filter_by(admin=True).first()
        if secrets.compare_digest(key_hash, db_key.key):
            return func(*args, **kwargs)
        raise Forbidden
    return wrapper

def require_sensor_key(func):
    def wrapper(self, sensor, *args, **kwargs):
        key_hash = ApiKey.key_hash(request.headers.get("Sensorhub-Api-Key").strip())
        db_key = ApiKey.query.filter_by(sensor=sensor).first()
        if db_key is not None and secrets.compare_digest(key_hash, db_key.key):
            return func(*args, **kwargs)
        raise Forbidden
    return wrapper


class SensorConverter(BaseConverter):
    
    def to_python(self, sensor_name):
        db_sensor = Sensor.query.filter_by(name=sensor_name).first()
        if db_sensor is None:
            raise NotFound
        return db_sensor
        
    def to_url(self, db_sensor):
        return db_sensor.name
