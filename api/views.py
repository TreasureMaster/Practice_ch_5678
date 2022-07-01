from flask import Blueprint, request, make_response, g, current_app, jsonify
from flask_restful import Api, Resource
from flask_httpauth import HTTPBasicAuth
from marshmallow import ValidationError, INCLUDE
from sqlalchemy.exc import SQLAlchemyError

from .models import db
from .schemas import (
    building_schema,
    chief_schema,
    department_schema,
    hall_schema,
    material_schema,
    target_schema,
    unit_schema,
    user_schema,
)
# from .db import get_db
from .api_exceptions import (
    BadRequestResourceError,
    NoInputDataError,
    NotFoundResourceError,
    NotUniqueDataError,
)
from . import status


# auth = HTTPBasicAuth()

# @auth.get_user_roles
# def get_user_roles(user):
#     # NOTE : user - это werkzeug.dataclasses.Authorization
#     user = User(get_db()).select_by_field('Login', user.username)
#     if user:
#         return 'admin' if user[0]['is_admin'] else 'user'
#     # NOTE если возвращает None, то будет отработан 403 FORBIDDEN

# @auth.verify_password
# def check_user_password(username, password):
#     if '!error' in UserModel(get_db()).sign_in(username, password):
#         return False
#     return True


api_bp = Blueprint('api', __name__)
api = Api(api_bp)

class AdminAuthRequired:
    """Добавляет аутентификацию администратора admin (как конфиг)"""
    # method_decorators = [auth.login_required(role='admin')]


class UserAuthRequiredResource(Resource):
    """Добавляет аутентификацию пользователя user (как ресурс)"""
    # method_decorators = [auth.login_required(role='user')]

# ------------------ Ресурс User без базовых классов ресурса ----------------- #
# class UserResource(Resource):
#     def get(self, id):
#         user = UserModel(get_db()).select_by_id(id)
#         if user is None:
#             raise NotFoundResourceError()
#             # return make_response(
#             #     {'errors': f'User with id={id} not found'},
#             #     status.HTTP_400_BAD_REQUEST
#             # )
#         user = user_schema.dump(user)
#         return user

#     def patch(self, id):
#         user_model = UserModel(get_db())
#         if user_model.select_by_id(id) is None:
#             raise NotFoundResourceError()

#         request_dict = request.get_json()
#         if not request_dict:
#             raise NoInputDataError()

#         try:
#             result = user_schema.load(request_dict, partial=True)
#         except ValidationError as e:
#             raise BadRequestResourceError(
#                 info={'errors': e.messages, 'valid': e.valid_data}
#             )

#         if 'login' in request_dict and not user_model.is_unique(id, request_dict['login']):
#             raise NotUniqueDataError(info={'field': 'login'})

#         user = user_model.update_by_id(id, **result)
#         return user_schema.dump(user)

#     def delete(self, id):
#         user_model = UserModel(get_db())
#         if user_model.select_by_id(id) is None:
#             raise NotFoundResourceError()
#         user_model.delete(id)
#         return make_response('', status.HTTP_204_NO_CONTENT)


# class UserListResource(Resource):
#     def get(self):
#         users = UserModel(get_db()).select_all()
#         users = user_schema.dump(users, many=True)
#         return users

#     def post(self):
#         request_dict = request.get_json()
#         if not request_dict:
#             raise NoInputDataError()
#             # resp = {'message': 'No input data provided'}
#             # return resp, status.HTTP_400_BAD_REQUEST

#         errors = user_schema.validate(request_dict)
#         if errors:
#             raise BadRequestResourceError(info=errors)
#             # return errors, status.HTTP_400_BAD_REQUEST

#         user_create = UserModel(get_db()).create(
#             **user_schema.load(request_dict)
#         )

#         if '!error' in user_create:
#             raise BadRequestResourceError(info={'login': user_create['!error']})

#         return user_schema.dump(user_create)


# -------------------------- Базовые классы ресурса -------------------------- #
class BaseResource(UserAuthRequiredResource):
    """Базовый класс ресурса (get, patch, delete)"""
    # method_decorators = [auth.login_required(role='user')]

    def get(self, id):
        entry = self._schema.model.query.get_or_404(id)
        return self._schema.dump(entry)

    def patch(self, id):
        entry = self._schema.model.query.get_or_404(id)

        request_dict = request.get_json()
        if not request_dict:
            raise NoInputDataError()

        # NOTE здесь и валидируем данные, и проверяем уникальность
        try:
            self._schema.context['raw_dict_return'] = True
            is_unique, error_fields = self._schema.model.check_unique(
                request_dict := self._schema.load(request_dict, partial=True), id
            )
        except ValidationError as e:
            raise BadRequestResourceError(
                info={'errors': e.messages, 'valid': e.valid_data}
            )
        else:
            if not is_unique:
                raise NotUniqueDataError(info={'fields': error_fields})

        try:
            entry.update(request_dict)
        except SQLAlchemyError as e:
            db.session.rollback()
            return make_response(
                jsonify({'error': str(e)}),
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        else:
            return make_response(
                self._schema.dump(entry),
                status.HTTP_200_OK
            )

    def delete(self, id):
        entity = self._schema.model.query.get_or_404(id)
        try:
            entity.delete()
        except SQLAlchemyError as e:
            db.session.rollback()
            return make_response(
                jsonify({'error': str(e)}),
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        else:
            return make_response(
                '',
                status.HTTP_204_NO_CONTENT
            )


class BaseListResource(UserAuthRequiredResource):
    """Базовый класс ресурса для списка (get, post)"""

    def get(self):
        entries = self._schema.model.query.all()
        return self._schema.dump(entries, many=True)

    def post(self):
        request_dict = request.get_json()
        if not request_dict:
            raise NoInputDataError()

        # NOTE здесь и валидируем данные, и проверяем уникальность
        try:
            self._schema.context['raw_dict_return'] = True
            is_unique, error_fields = self._schema.model.check_unique(
                self._schema.load(request_dict)
            )
        except ValidationError as e:
            raise BadRequestResourceError(
                info={'errors': e.messages, 'valid': e.valid_data}
            )
        else:
            if not is_unique:
                raise NotUniqueDataError(info={'fields': error_fields})
            # Теперь нужно загрузить сам объект (без контекста схемы), а не его словарь
            new_entry = self._schema.load(request_dict)

        try:
            new_entry.create()
        except SQLAlchemyError as e:
            db.session.rollback()
            return make_response(
                jsonify({'error': str(e)}),
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        else:
            return make_response(
                self._schema.dump(new_entry),
                status.HTTP_201_CREATED
            )


# ---------------------- Инициализация целевых ресурсов ---------------------- #
class UserBaseConfig(AdminAuthRequired):
    _schema = user_schema
    # method_decorators = [auth.login_required(role='admin')]


class UserResource(UserBaseConfig, BaseResource):
    """."""
    # method_decorators = [auth.login_required(role='admin')]


class UserListResource(UserBaseConfig, BaseListResource):
    """."""


class TargetBaseConfig:
    _schema = target_schema


class TargetResource(TargetBaseConfig, BaseResource):
    """."""


class TargetListResource(TargetBaseConfig, BaseListResource):
    """."""


class MaterialBaseConfig:
    _schema = material_schema


class MaterialResource(MaterialBaseConfig, BaseResource):
    """."""


class MaterialListResource(MaterialBaseConfig, BaseListResource):
    """."""


class DepartmentBaseConfig:
    _schema = department_schema


class DepartmentResource(DepartmentBaseConfig, BaseResource):
    """."""


class DepartmentListResource(DepartmentBaseConfig, BaseListResource):
    """."""


class BuildingBaseConfig:
    _schema = building_schema


class BuildingResource(BuildingBaseConfig, BaseResource):
    """."""


class BuildingListResource(BuildingBaseConfig, BaseListResource):
    """."""


# class HallBaseConfig:
#     _model = HallModel
#     _schema = hall_schema
#     # None нужно делать, чтобы не путаться с уникальными полями
#     _unique_key = None


# class HallResource(HallBaseConfig, BaseResource):
#     """."""


# class HallListResource(HallBaseConfig, BaseListResource):
#     """."""


# class ChiefBaseConfig:
#     _model = ChiefModel
#     _schema = chief_schema
#     # None нужно делать, чтобы не путаться с уникальными полями
#     _unique_key = None


# class ChiefResource(ChiefBaseConfig, BaseResource):
#     """."""


# class ChiefListResource(ChiefBaseConfig, BaseListResource):
#     """."""


# class UnitBaseConfig:
#     _model = UnitModel
#     _schema = unit_schema
#     # None нужно делать, чтобы не путаться с уникальными полями
#     _unique_key = None


# class UnitResource(UnitBaseConfig, BaseResource):
#     """."""


# class UnitListResource(UnitBaseConfig, BaseListResource):
#     """."""


# --------------------------------- Маршруты --------------------------------- #
api.add_resource(UserListResource, '/users/')
api.add_resource(UserResource, '/users/<int:id>')
api.add_resource(TargetListResource, '/targets/')
api.add_resource(TargetResource, '/targets/<int:id>')
api.add_resource(MaterialListResource, '/materials/')
api.add_resource(MaterialResource, '/materials/<int:id>')
api.add_resource(DepartmentListResource, '/departments/')
api.add_resource(DepartmentResource, '/departments/<int:id>')
api.add_resource(BuildingListResource, '/buildings/')
api.add_resource(BuildingResource, '/buildings/<int:id>')
# api.add_resource(HallListResource, '/halls/')
# api.add_resource(HallResource, '/halls/<int:id>')
# api.add_resource(ChiefListResource, '/chiefs/')
# api.add_resource(ChiefResource, '/chiefs/<int:id>')
# api.add_resource(UnitListResource, '/units/')
# api.add_resource(UnitResource, '/units/<int:id>')
