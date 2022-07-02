# Запуск приложения Flask - .\run
$env:FLASK_APP="api.app:create_app('api.config')"
$env:FLASK_ENV="development"
# Param(
#     [string]$message = ""
# )
flask db migrate -m "$($args[0])"
flask db upgrade
