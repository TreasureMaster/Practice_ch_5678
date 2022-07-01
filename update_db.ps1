# Запуск приложения Flask - .\run
$env:FLASK_APP="api.app:create_app('api.config')"
$env:FLASK_ENV="development"
param(
    [string]$message = ""
)
flask db migrate -m $message
flask db upgrade
