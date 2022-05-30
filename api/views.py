from flask import Blueprint, make_response
from flask_restful import Api, Resource

from .models import UserModel
from .schemas import user_schema
from .db import get_db
from . import status


api_bp = Blueprint('api', __name__)
api = Api(api_bp)


class UserResource(Resource):
    def get(self, id):
        user = UserModel(get_db()).select_by_id(id)
        if user is None:
            return make_response(
                {'errors': f'User with id={id} not found'},
                status.HTTP_400_BAD_REQUEST
            )
        user = user_schema.dump(user)
        return user


class UserListResource(Resource):
    def get(self):
        users = UserModel(get_db()).select_all()
        users = user_schema.dump(users, many=True)
        return users


api.add_resource(UserListResource, '/users/')
api.add_resource(UserResource, '/users/<int:id>')