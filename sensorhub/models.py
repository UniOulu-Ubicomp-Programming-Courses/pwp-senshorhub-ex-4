import datetime
import click
import hashlib
from flask.cli import with_appcontext
from sensorhub import db

deployments = db.Table(
    "deployments",
    db.Column("deployment_id", db.Integer, db.ForeignKey("deployment.id"), primary_key=True),
    db.Column("sensor_id", db.Integer, db.ForeignKey("sensor.id"), primary_key=True)
)

class ApiKey(db.Model):
    
    key = db.Column(db.LargeBinary, nullable=False, unique=True, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("sensor.id"), nullable=True)
    admin =  db.Column(db.Boolean, default=False)
    
    sensor = db.relationship("Sensor", uselist=False)
    
    @staticmethod
    def key_hash(key):
        return hashlib.sha256(key.encode()).digest()


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    altitude = db.Column(db.Float, nullable=True)
    description=db.Column(db.String(256), nullable=True)

    sensor = db.relationship("Sensor", back_populates="location", uselist=False)

    def serialize(self, short_form=False):
        doc = {
            "name": self.name
        }
        if not short_form:
            doc["longitude"] = self.longitude
            doc["latitude"] = self.latitude
            doc["altitude"] = self.altitude
            doc["description"] = self.description
        return doc

    def deserialize(self, doc):
        self.name = doc["name"]
        self.latitude = doc.get("latitude")
        self.longitude = doc.get("longitude")
        self.altitude = doc.get("altitude")
        self.description = doc.get("description")


class Deployment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(128), nullable=False)

    sensors = db.relationship("Sensor", secondary=deployments, back_populates="deployments")


class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True)
    model = db.Column(db.String(128), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey("location.id"), unique=True)

    location = db.relationship("Location", back_populates="sensor")
    measurements = db.relationship("Measurement", back_populates="sensor")
    deployments = db.relationship("Deployment", secondary=deployments, back_populates="sensors")
    stats = db.relationship("Stats", back_populates="sensor", uselist=False)

    def serialize(self, short_form=False):
        return {
            "name": self.name,
            "model": self.model,
            "location": self.location and self.location.serialize(short_form=short_form)
        }

    def deserialize(self, doc):
        self.name = doc["name"]
        self.model = doc["model"]

    @staticmethod
    def json_schema():
        schema = {
            "type": "object",
            "required": ["name", "model"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Sensor's unique name",
            "type": "string"
        }
        props["model"] = {
            "description": "Name of the sensor's model",
            "type": "string"
        }
        return schema


class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("sensor.id", ondelete="SET NULL"))
    value = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime, nullable=False)

    sensor = db.relationship("Sensor", back_populates="measurements")

    @staticmethod
    def json_schema():
        schema = {
            "type": "object",
            "required": ["value"]
        }
        props = schema["properties"] = {}
        props["value"] = {
            "description": "Measured value.",
            "type": "number"
        }
        props["time"] = {
            "description": "Measurement timestamp",
            "type": "string",
            "pattern": "^[0-9]{4}-[01][0-9]-[0-3][0-9]T[0-9]{2}:[0-5][0-9]:[0-5][0-9]Z$"
        }
        return schema


class Stats(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    generated = db.Column(db.DateTime, nullable=False)
    mean = db.Column(db.Float, nullable=False)
    sensor_id = db.Column(
        db.Integer,
        db.ForeignKey("sensor.id"),
        unique=True, nullable=False
    )

    sensor = db.relationship("Sensor", back_populates="stats")

    def serialize(self):
        return {
            "generated": self.generated.isoformat(),
            "mean": self.mean
        }

    def deserialize(self, doc):
        self.generated = datetime.datetime.fromisoformat(doc["generated"])
        self.mean = doc["mean"]

    @staticmethod
    def json_schema():
        schema = {
            "type": "object",
            "required": ["generated", "mean"]
        }
        props = schema["properties"] = {}
        props["generated"] = {
            "description": "Generation timestamp",
            "type": "string",
            "format": "date-time"
        }
        props["mean"] = {
            "description": "Mean value of data",
            "type": "number"
        }
        return schema


@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()

@click.command("testgen")
@with_appcontext
def generate_test_data():
    import datetime
    import random
    s = Sensor(
        name="test-sensor-1",
        model="testsensor"
    )
    now = datetime.datetime.now()
    interval = datetime.timedelta(seconds=10)
    for i in range(1000):
        m = Measurement(
            value=round(random.random() * 100, 2),
            time=now
        )
        now += interval
        s.measurements.append(m)
    
    db.session.add(s)
    db.session.commit()

@click.command("masterkey")
@with_appcontext
def generate_master_key():
    import secrets
    token = secrets.token_urlsafe()
    db_key = ApiKey(
        key=ApiKey.key_hash(token),
        admin=True
    )
    db.session.add(db_key)
    db.session.commit()
    print(token)
