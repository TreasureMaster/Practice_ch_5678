from flask import g, current_app

from .models import PGCursor


def get_db():
    if 'db' not in g:
        g.db = PGCursor()

    return g.db

# @current_app.teardown_appcontext
# def teardown_db(exception):
#     db = g.pop('db', None)

#     if db is not None:
#         db.close()