from flask import Flask, g


def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)

    from .db import get_db
    with app.app_context():
        get_db()
    # db.init_app(app)

    # from .views import api_bp
    # app.register_blueprint(api_bp, url_prefix='/api')

    return app
