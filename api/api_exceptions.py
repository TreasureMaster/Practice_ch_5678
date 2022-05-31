from flask_apiexceptions import ApiException

from . import status


class NotFoundResourceError(ApiException):
    status_code = status.HTTP_404_NOT_FOUND
    code = 'not-found'


class UserNotFoundError(NotFoundResourceError):
    message = 'User with such id not found.'


api_exceptions = (
    UserNotFoundError,
)