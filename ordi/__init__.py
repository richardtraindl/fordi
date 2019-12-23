
import os

from flask import Flask

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'ordi.sqlite'),
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

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import ordi
    app.register_blueprint(ordi.bp)
    app.add_url_rule('/', endpoint='index')

    return app
    
    #app.config.from_mapping(
    #    SECRET_KEY='dev',
        #DATABASE=os.path.join(app.instance_path, 'Ordi.mdb'),
    #)

    #if(test_config is None):
        # load the instance config, if it exists, when not testing
    #    app.config.from_pyfile('config.py', silent=True)
    #else:
        # load the test config if passed in
    #    app.config.from_mapping(test_config)

    # ensure the instance folder exists
    #try:
    #    os.makedirs(app.instance_path)
    #except OSError:
    #    pass

    #from . import db
    #db.init_app(app)

    #from . import auth
    #app.register_blueprint(auth.bp)

    #from app import routes
    #from . import ordi
    #app.register_blueprint(ordi.bp)
    #app.add_url_rule('/', endpoint='index')

    #from .util.filters import fmttime, mapstatus, maplevel, iseven, reverseview
    #app.jinja_env.filters['fmttime'] = fmttime
    #app.jinja_env.filters['mapstatus'] = mapstatus
    #app.jinja_env.filters['maplevel'] = maplevel
    #app.jinja_env.filters['iseven'] = iseven
    #app.jinja_env.filters['reverseview'] = reverseview

    #return app
 

