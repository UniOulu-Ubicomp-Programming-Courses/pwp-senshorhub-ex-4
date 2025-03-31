import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from sensorhub.constants import *

db = SQLAlchemy()
cache = Cache()

# Based on http://flask.pocoo.org/docs/1.0/tutorial/factory/#the-application-factory
# Modified to use Flask SQLAlchemy
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "development.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        CACHE_TYPE="FileSystemCache",
        CACHE_DIR=os.path.join(app.instance_path, "cache"),
        RABBITMQ_BROKER_ADDR="amqp://localhost/",
        RABBIT_USE_TLS=False,
    )

    if test_config is None:
        app.config.from_pyfile("config/config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    cache.init_app(app)

    from . import models
    from . import api
    from sensorhub.utils import SensorConverter
    app.cli.add_command(models.init_db_command)
    app.cli.add_command(models.generate_test_data)
    app.cli.add_command(models.generate_master_key)
    app.url_map.converters["sensor"] = SensorConverter
    app.register_blueprint(api.api_bp)

    return app
