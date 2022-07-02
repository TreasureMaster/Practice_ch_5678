import http

from flask_apiexceptions import ApiException


# ---------------------------------- Код 400 --------------------------------- #
class BadRequestResourceError(ApiException):
    status_code = http.HTTPStatus.BAD_REQUEST
    code = 'bad-request'
    message = 'Bad request error'


class NoInputDataError(BadRequestResourceError):
    code = 'no-input-data'
    message = 'No input data provided'


class NotUniqueDataError(BadRequestResourceError):
    code = 'not-unique'
    message = 'Field must be unique'


# ---------------------------------- Код 404 --------------------------------- #
class NotFoundResourceError(ApiException):
    status_code = http.HTTPStatus.NOT_FOUND
    code = 'not-found'
    message = 'Field with such id not found'


# class UserNotFoundError(NotFoundResourceError):


api_exceptions = (
    BadRequestResourceError,
    NoInputDataError,
    NotFoundResourceError,
    NotUniqueDataError,
)