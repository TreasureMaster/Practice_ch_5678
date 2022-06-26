import os


basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG = True
PORT = 5000
HOST = '127.0.0.1'

# False - не регистрирует операторы, отправленные в stderr
SQLALCHEMY_ECHO = False
# True - отслеживать модификацию объектов
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = "postgresql://{DB_USER}:{DB_PASS}@{DB_ADDR}/{DB_NAME}".format(
    DB_USER='postgres',
    DB_PASS='root',
    DB_ADDR='127.0.0.1',
    DB_NAME='estate_register',
)
# вроде бы настройка sqlalchemy-migrate
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# Глобальные параметры разбиения на страницы пагинации
# Количество записей на странице
# PAGINATION_PAGE_SIZE = 5
# Название настройки в запросах для указания страницы, которую нужно получить
# PAGINATION_PAGE_ARGUMENT_NAME = 'page'
