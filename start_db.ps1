# Запуск приложения Flask - .\run
$env:FLASK_APP="api.app:create_app('api.config')"
$env:FLASK_ENV="development"
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
