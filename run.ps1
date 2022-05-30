# Запуск приложения Flask - .\run
$env:FLASK_APP="api.app:create_app('api.config')"
$env:FLASK_ENV="development"
flask run