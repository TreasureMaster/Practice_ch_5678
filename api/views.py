from flask import Blueprint, request, make_response, g, current_app
from flask_restful import Api, Resource
from flask_httpauth import HTTPBasicAuth
from marshmallow import ValidationError

from .models import (
    BuildingModel,
    ChiefModel,
    DepartmentModel,
    HallModel,
    MaterialModel,
    TargetModel,
    UnitModel,
    UserModel,
)
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
from .db import get_db
from .api_exceptions import (
    BadRequestResourceError,
    NoInputDataError,
    NotFoundResourceError,
    NotUniqueDataError,
)
from . import status


auth = HTTPBasicAuth()

@auth.get_user_roles
def get_user_roles(user):
    # NOTE : user - это werkzeug.dataclasses.Authorization
    user = UserModel(get_db()).select_by_field('Login', user.username)
    if user:
        return 'admin' if user[0]['is_admin'] else 'user'
    # NOTE если возвращает None, то будет отработан 403 FORBIDDEN

@auth.verify_password
def check_user_password(username, password):
    if '!error' in UserModel(get_db()).sign_in(username, password):
        return False
    return True


api_bp = Blueprint('api', __name__)
api = Api(api_bp)

class AdminAuthRequired:
    """Добавляет аутентификацию администратора admin (как конфиг)"""
    method_decorators = [auth.login_required(role='admin')]


class UserAuthRequiredResource(Resource):
    """Добавляет аутентификацию пользователя user (как ресурс)"""
    method_decorators = [auth.login_required(role='user')]

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
        model = self._model(get_db())
        if not (target := model.select_by_id(id)):
            raise NotFoundResourceError(info={'id': id})

        # print(target)
        return self._schema.dump(target)
        # print(a)
        # return a

    def patch(self, id):
        model = self._model(get_db())
        if model.select_by_id(id) is None:
            raise NotFoundResourceError()

        request_dict = request.get_json()
        if not request_dict:
            raise NoInputDataError()

        try:
            result = self._schema.load(request_dict, partial=True)
        except ValidationError as e:
            raise BadRequestResourceError(
                info={'errors': e.messages, 'valid': e.valid_data}
            )

        if (
            self._unique_key is not None and
            self._unique_key in request_dict and
            not model.is_unique(id, request_dict[self._unique_key])
        ):
            raise NotUniqueDataError(info={'field': self._unique_key})

        entry = model.update_by_id(id, **result)
        # FIXME с этим пока ошибка, так как возвращает неполные данные (исправить с SQLALchemy)
        return self._schema.dump(entry)

    def delete(self, id):
        model = self._model(get_db())
        if model.select_by_id(id) is None:
            raise NotFoundResourceError(info={'id': id})
        model.delete(id)
        return make_response('', status.HTTP_204_NO_CONTENT)


class BaseListResource(UserAuthRequiredResource):
    """Базовый класс ресурса для списка (get, post)"""
    # method_decorators = [auth.login_required(role='user')]

    def get(self):
        entries = self._model(get_db()).select_all()
        return self._schema.dump(entries, many=True)

    def post(self):
        request_dict = request.get_json()
        if not request_dict:
            raise NoInputDataError()

        try:
            result = self._schema.load(request_dict)
        except ValidationError as e:
            raise BadRequestResourceError(
                info={'errors': e.messages, 'valid': e.valid_data}
            )

        model = self._model(get_db())
        if (
            self._unique_key is not None and
            self._unique_key in request_dict and
            not model.is_unique(id, request_dict[self._unique_key])
        ):
            raise NotUniqueDataError(info={'field': self._unique_key})

        entry_create = model.create(**result)
        # FIXME с этим пока ошибка, так как возвращает неполные данные (исправить с SQLALchemy)
        return self._schema.dump(entry_create)


# ---------------------- Инициализация целевых ресурсов ---------------------- #
class UserBaseConfig(AdminAuthRequired):
    _model = UserModel
    _schema = user_schema
    _unique_key = 'login'
    # method_decorators = [auth.login_required(role='admin')]


class UserResource(UserBaseConfig, BaseResource):
    """."""
    # method_decorators = [auth.login_required(role='admin')]


class UserListResource(UserBaseConfig, BaseListResource):
    """."""


class TargetBaseConfig:
    _model = TargetModel
    _schema = target_schema
    _unique_key = 'target'


class TargetResource(TargetBaseConfig, BaseResource):
    """."""


class TargetListResource(TargetBaseConfig, BaseListResource):
    """."""


class MaterialBaseConfig:
    _model = MaterialModel
    _schema = material_schema
    _unique_key = 'material'


class MaterialResource(MaterialBaseConfig, BaseResource):
    """."""


class MaterialListResource(MaterialBaseConfig, BaseListResource):
    """."""


class DepartmentBaseConfig:
    _model = DepartmentModel
    _schema = department_schema
    # None нужно делать, чтобы не путаться с уникальными полями
    _unique_key = None


class DepartmentResource(DepartmentBaseConfig, BaseResource):
    """."""


class DepartmentListResource(DepartmentBaseConfig, BaseListResource):
    """."""


class BuildingBaseConfig:
    _model = BuildingModel
    _schema = building_schema
    # None нужно делать, чтобы не путаться с уникальными полями
    _unique_key = None


class BuildingResource(BuildingBaseConfig, BaseResource):
    """."""


class BuildingListResource(BuildingBaseConfig, BaseListResource):
    """."""


class HallBaseConfig:
    _model = HallModel
    _schema = hall_schema
    # None нужно делать, чтобы не путаться с уникальными полями
    _unique_key = None


class HallResource(HallBaseConfig, BaseResource):
    """."""


class HallListResource(HallBaseConfig, BaseListResource):
    """."""


class ChiefBaseConfig:
    _model = ChiefModel
    _schema = chief_schema
    # None нужно делать, чтобы не путаться с уникальными полями
    _unique_key = None


class ChiefResource(ChiefBaseConfig, BaseResource):
    """."""


class ChiefListResource(ChiefBaseConfig, BaseListResource):
    """."""


class UnitBaseConfig:
    _model = UnitModel
    _schema = unit_schema
    # None нужно делать, чтобы не путаться с уникальными полями
    _unique_key = None


class UnitResource(UnitBaseConfig, BaseResource):
    """."""


class UnitListResource(UnitBaseConfig, BaseListResource):
    """."""


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
api.add_resource(HallListResource, '/halls/')
api.add_resource(HallResource, '/halls/<int:id>')
api.add_resource(ChiefListResource, '/chiefs/')
api.add_resource(ChiefResource, '/chiefs/<int:id>')
api.add_resource(UnitListResource, '/units/')
api.add_resource(UnitResource, '/units/<int:id>')
