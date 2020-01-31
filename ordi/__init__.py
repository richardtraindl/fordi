
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY = 'dev',
        #SQLALCHEMY_DATABASE_URI = 'sqlite:///C:\\wse4\\flask\\instance\\ordi.sqlite',
        SQLALCHEMY_DATABASE_URI = 'sqlite:////home/richard/dev/flask/fordi/instance/ordi.sqlite',
        SQLALCHEMY_TRACK_MODIFICATIONS = False,
        SEND_FILE_MAX_AGE_DEFAULT = 0
    )


    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db = SQLAlchemy(app)
    migrate = Migrate(app, db)

    from . import db2
    db2.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import ordi
    app.register_blueprint(ordi.bp)
    app.add_url_rule('/', endpoint='index')

    from .util.filters import mapanrede, mapgeschlecht, mapartikel, filter_supress_none
    app.jinja_env.filters['mapanrede'] = mapanrede
    app.jinja_env.filters['mapgeschlecht'] = mapgeschlecht
    app.jinja_env.filters['mapartikel'] = mapartikel
    app.jinja_env.filters['sn'] = filter_supress_none

    return app
