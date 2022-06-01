from flask import Blueprint, request, make_response
from flask_restful import Api, Resource
from marshmallow import ValidationError

from .models import UserModel, TargetModel
from .schemas import (
    target_schema,
    user_schema,
)
from .db import get_db
from .api_exceptions import (
    BadRequestResourceError,
    NoInputDataError,
    NotFoundResourceError,
    NotUniqueDataError,
)
from . import status


api_bp = Blueprint('api', __name__)
api = Api(api_bp)


class UserResource(Resource):
    def get(self, id):
        user = UserModel(get_db()).select_by_id(id)
        if user is None:
            raise NotFoundResourceError()
            # return make_response(
            #     {'errors': f'User with id={id} not found'},
            #     status.HTTP_400_BAD_REQUEST
            # )
        user = user_schema.dump(user)
        return user

    def patch(self, id):
        user_model = UserModel(get_db())
        if user_model.select_by_id(id) is None:
            raise NotFoundResourceError()

        request_dict = request.get_json()
        if not request_dict:
            raise NoInputDataError()

        try:
            result = user_schema.load(request_dict, partial=True)
        except ValidationError as e:
            raise BadRequestResourceError(
                info={'errors': e.messages, 'valid': e.valid_data}
            )

        if 'login' in request_dict and not user_model.is_unique(id, request_dict['login']):
            raise NotUniqueDataError(info={'field': 'login'})

        user = user_model.update_by_id(id, **result)
        return user_schema.dump(user)

    def delete(self, id):
        user_model = UserModel(get_db())
        if user_model.select_by_id(id) is None:
            raise NotFoundResourceError()
        user_model.delete(id)
        return make_response('', status.HTTP_204_NO_CONTENT)


class UserListResource(Resource):
    def get(self):
        users = UserModel(get_db()).select_all()
        users = user_schema.dump(users, many=True)
        return users

    def post(self):
        request_dict = request.get_json()
        if not request_dict:
            raise NoInputDataError()
            # resp = {'message': 'No input data provided'}
            # return resp, status.HTTP_400_BAD_REQUEST

        errors = user_schema.validate(request_dict)
        if errors:
            raise BadRequestResourceError(info=errors)
            # return errors, status.HTTP_400_BAD_REQUEST

        user_create = UserModel(get_db()).create(
            **user_schema.load(request_dict)
        )

        if '!error' in user_create:
            raise BadRequestResourceError(info={'login': user_create['!error']})

        return user_schema.dump(user_create)


class TargetResource(Resource):
    def get(self, id):
        target_model = TargetModel(get_db())
        if not (target := target_model.select_by_id(id)):
            raise NotFoundResourceError(info={'id': id})

        return target_schema.dump(target)

    def patch(self, id):
        target_model = TargetModel(get_db())
        if target_model.select_by_id(id) is None:
            raise NotFoundResourceError()

        request_dict = request.get_json()
        if not request_dict:
            raise NoInputDataError()

        try:
            result = target_schema.load(request_dict, partial=True)
        except ValidationError as e:
            raise BadRequestResourceError(
                info={'errors': e.messages, 'valid': e.valid_data}
            )

        if 'target' in request_dict and not target_model.is_unique(id, request_dict['target']):
            raise NotUniqueDataError(info={'field': 'target'})

        target = target_model.update_by_id(id, **result)
        return target_schema.dump(target)

    def delete(self, id):
        target_model = TargetModel(get_db())
        if target_model.select_by_id(id) is None:
            raise NotFoundResourceError(info={'id': id})
        target_model.delete(id)
        return make_response('', status.HTTP_204_NO_CONTENT)


class TargetListResource(Resource):
    def get(self):
        targets = TargetModel(get_db()).select_all()
        return target_schema.dump(targets, many=True)

    def post(self):
        request_dict = request.get_json()
        if not request_dict:
            raise NoInputDataError()

        try:
            result = target_schema.load(request_dict)
        except ValidationError as e:
            raise BadRequestResourceError(
                info={'errors': e.messages, 'valid': e.valid_data}
            )

        target_model = TargetModel(get_db())
        if 'target' in request_dict and not target_model.is_unique(0, request_dict['target']):
            raise NotUniqueDataError(info={'field': 'target'})

        target_create = target_model.create(**result)

        return target_schema.dump(target_create)


api.add_resource(UserListResource, '/users/')
api.add_resource(UserResource, '/users/<int:id>')
api.add_resource(TargetListResource, '/targets/')
api.add_resource(TargetResource, '/targets/<int:id>')