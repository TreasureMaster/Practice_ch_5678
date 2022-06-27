# from models import db_init
from api.models import db
from api.app import create_app


if __name__ == '__main__':
    # db_init()
    db.create_all(app=create_app('api.config'))
    # FIXME таблицы до конца не построены, поэтому не работает
    # db.drop_all(app=create_app('api.config'))