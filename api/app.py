from flask import Flask, g
from flask_apiexceptions import JSONExceptionHandler, api_exception_handler


def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)

    exc_extension = JSONExceptionHandler(app)

    from .api_exceptions import api_exceptions
    [
        exc_extension.register(
            code_or_exception=exc,
            handler=api_exception_handler
        )
        for exc in api_exceptions
    ]

    # from .models.models import db
    from .models import db
    db.init_app(app)

    # from .db import get_db
    # with app.app_context():
    #     get_db()
    # db.init_app(app)

    from .views import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
