import datetime as dt

from psycopg2 import sql
import marshmallow as mm
import marshmallow.validate as mmv

from .basemodel import BaseModel, RequiredField, backref, ComposedProperty


class UserModel(BaseModel):
    """Модель пользователя"""
    _table = 'users'
    _entity_name = 'Пользователь'
    _primary_key = 'IDUser'
    _fields = {
        'Login': RequiredField(),
        'Password': RequiredField(),
        'is_admin': False
    }
    class ValidateSchema(mm.Schema):
        """Схема валидации модели."""
        Login = mm.fields.String(required=True)
        Password = mm.fields.String(required=True)
        is_admin = mm.fields.Boolean(required=True)

    def sign_in(self, login, password):
        """Вход в программу"""
        stmt = sql.SQL('SELECT * FROM {} WHERE {}={}').format(
            sql.Identifier(self._table),
            sql.Identifier('Login'),
            sql.Literal(login)
        )
        row = self.execute_get_one(stmt)
        if not row:
            return {'!error': f'Пользователя с логином "{login}" не существует'}
        if row['Password'] != self.encrypt(password):
            return {'!error': f'Введенный пароль не совпадает'}

        return {'is_admin': row['is_admin']}

    def create(self, **input_fields):
        """Добавление нового пользователя"""
        # проверка вставки дубликата уникальных имен
        if self.select_by_field('Login', input_fields['Login']):
            return {'!error': f'''Пользователь с логином "{input_fields['Login']}" уже существует'''}
        return super().create(**input_fields)


class MaterialModel(BaseModel):
    """Модель материала здания"""
    _table = 'materials'
    _entity_name = 'Материал'
    _primary_key = 'IDMaterial'
    _fields = {
        'Material': RequiredField(),
    }


class TargetModel(BaseModel):
    """Модель назначения помещения"""
    _table = 'targets'
    _entity_name = 'Тип помещения'
    _primary_key = 'IDTarget'
    _fields = {
        'Target': RequiredField(),
    }


class DepartmentModel(BaseModel):
    """Модель кафедры"""
    _table = 'departments'
    _entity_name = 'Кафедра'
    _primary_key = 'IDDepartment'
    _fields = {
        'DepartmentName': RequiredField(),
        'Boss': RequiredField(),
        'Phone': RequiredField(),
        'OfficeDean': RequiredField(),
    }
    class ValidateSchema(mm.Schema):
        """Схема валидации модели."""
        DepartmentName = mm.fields.String(required=True)
        Boss = mm.fields.String(required=True)
        Phone = mm.fields.Integer(required=True)
        OfficeDean = mm.fields.String(required=True)


class BuildingModel(BaseModel):
    """Модель здания"""
    _table = 'buildings'
    _entity_name = 'Здание'
    _primary_key = 'IDKadastr'
    _fields = {
        'BuildingName': RequiredField(),
        'Land': RequiredField(),
        'Address': RequiredField(),
        'Year': RequiredField(),
        'Wear': RequiredField(),
        'Flow': RequiredField(),
        'Picture': None,
        'Comment': None,
        'MaterialID': backref(MaterialModel),
    }
    class ValidateSchema(mm.Schema):
        """Схема валидации модели."""
        BuildingName = mm.fields.String(required=True)
        Land = mm.fields.Float(required=True)
        Address = mm.fields.String(required=True)
        Year = mm.fields.Integer(required=True, validate=mmv.Range(min=1600, max=dt.datetime.now().year))
        Wear = mm.fields.Integer(required=True, validate=mmv.Range(min=0, max=100))
        Flow = mm.fields.Integer(required=True, validate=mmv.Range(min=1, max=100))
        Picture = mm.fields.String(allow_none=True)
        Comment = mm.fields.String(allow_none=True)

        class Meta:
            unknown = mm.EXCLUDE


class HallModel(BaseModel):
    """Модель помещения"""
    _table = 'halls'
    _entity_name = 'Помещение'
    _primary_key = 'IDHall'
    _fields = {
        'HallNumber': RequiredField(),
        'HallSquare': RequiredField(),
        'Windows': RequiredField(),
        'Heaters': RequiredField(),
        'TargetID': backref(TargetModel),
        'DepartmentID': backref(DepartmentModel),
        'KadastrID': backref(BuildingModel),
        'HallName': ComposedProperty(
            # из какой таблицы брать
            _table,
            {
                # название свойства, с которым оно будет возвращаться из БД
                'title': 'HallName',
                # объединяемые поля в псоледовательности объединения
                'fields': ('HallNumber', 'targets.Target', 'buildings.BuildingName'),# 'HouseNumber'),
                # разделитель полей при объединении (по умолчанию - пробел)
                'sep': ', ',
            }
        ),
    }
    class ValidateSchema(mm.Schema):
        """Схема валидации модели."""
        HallNumber = mm.fields.Integer(required=True, validate=mmv.Range(min=0))
        HallSquare = mm.fields.Float(required=True)
        Windows = mm.fields.Integer(required=True, validate=mmv.Range(min=0))
        Heaters = mm.fields.Integer(required=True, validate=mmv.Range(min=0))

        class Meta:
            unknown = mm.EXCLUDE


class ChiefModel(BaseModel):
    """Модель ответственного"""
    _table = 'chiefs'
    _entity_name = 'Ответственный'
    _primary_key = 'IDChief'
    _fields = {
        'Chief': RequiredField(),
        'AddressChief': RequiredField(),
        'Experience': RequiredField(),
    }
    class ValidateSchema(mm.Schema):
        """Схема валидации модели."""
        Chief = mm.fields.String(required=True)
        AddressChief = mm.fields.String(required=True)
        Experience = mm.fields.Integer(required=True, validate=mmv.Range(min=0))


class UnitModel(BaseModel):
    """Модель имущества"""
    _table = 'units'
    _entity_name = 'Имущество'
    _primary_key = 'IDUnit'
    _fields = {
        'UnitName': RequiredField(),
        'DateStart': RequiredField(),
        'Cost': RequiredField(),
        'CostYear': RequiredField(),
        'CostAfter': RequiredField(),
        'Period': RequiredField(),
        'HallID': backref(HallModel),
        'ChiefID': backref(ChiefModel),
    }
    class ValidateSchema(mm.Schema):
        """Схема валидации модели."""
        UnitName = mm.fields.String(required=True)
        DateStart = mm.fields.Date(required=True)
        Cost = mm.fields.Float(required=True)
        CostYear = mm.fields.Integer(required=True, validate=mmv.Range(min=1600, max=dt.datetime.now().year))
        CostAfter = mm.fields.Float(required=True)
        Period = mm.fields.Integer(required=True, validate=mmv.Range(min=0))

        class Meta:
            unknown = mm.EXCLUDE
