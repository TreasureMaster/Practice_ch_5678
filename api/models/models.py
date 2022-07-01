import datetime as dt
import typing as t

from collections import OrderedDict

import sqlalchemy as sa
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect


db = SQLAlchemy()


class OperationMixin:
    # список полей, которые нужно шифровать перед записью в БД
    _secret_fields = ()
    # список уникальных полей, которые нужно проверять, игнорируя регистр символов
    _icase_unique_fields = ()

    def _add(self):
        """Общий метод добавления объекта в сессию и его фиксацию"""
        db.session.add(self)
        db.session.commit()

    def create(self):
        """Создает объект в БД"""
        self._add()

    def update(
        self,
        patched_fields: t.Union[dict, OrderedDict]
    ) -> None:
        """Обновляет объект в БД"""
        for field, value in patched_fields.items():
            setattr(self, field, value)
        self._add()

    def delete(self):
        """Удаляет объект из БД"""
        db.session.delete(self)
        db.session.commit()

    def encrypting(self):
        """Шифрование полей, которые должны быть зашифрованы перед помещением в БД"""
        for field in self._secret_fields:
            if getattr(self, field, None) is not None:
                setattr(self, field, generate_password_hash(getattr(self, field)))
        return self

    @classmethod
    def check_unique(
        cls,
        fields: t.Union[dict, OrderedDict],
        pk: t.Optional[int] = None
    ) -> t.Tuple[bool, tuple]:
        """Проверяет уникальность всех уникальных полей модели."""
        pk_name = cls.get_primary().name
        uniques = [
            # Добавляем имя (ошибка), если оно не уникально, кроме случая патча самого себя
            c.name if (pk is None or pk != getattr(e, pk_name)) else False
            for c in inspect(cls).columns
            if (
                # Есть ли уникальные поля в модели ?
                c.unique and
                # Получить значение уникального поля проверяемой сущности
                (attr := fields.get(c.name, None)) is not None and
                # Проверить есть ли уже такое значение в БД
                (e := cls.get_not_unique(c, attr)) is not None
            )
        ]
        if any(uniques):
            return False, uniques
        return True, ()

    @classmethod
    def get_primary(cls):
        """Возвращает объект колонки первичного ключа"""
        # NOTE реализация только для простого первичного ключа (не составного)
        return inspect(cls).primary_key[0]

    @classmethod
    def get_not_unique(
        cls,
        column: sa.Column,
        attr: t.Any,
    ) -> t.Optional[db.Model]:
        """Возвращает первое попавшееся не уникальное поле для заданной колонки
        или None, если его нет.
        """
        if column.name in cls._icase_unique_fields:
            return cls.query.filter(func.lower(column) == attr.lower()).first()
        return cls.query.filter(column == attr).first()

    # @classmethod
    # def get_last_item(cls):
    #     """Возвращает последнюю вставленную запись"""
    #     return cls.query.order_by(cls.get_primary().desc()).first()


class User(db.Model, OperationMixin):
    """Модель пользователя"""
    __tablename__ = 'users'
    _secret_fields = ('Password',)
    _icase_unique_fields = ('Login',)

    IDUser = db.Column(db.Integer, primary_key=True)
    Login = db.Column(db.String(32), nullable=False, unique=True)
    Password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self) -> str:
        return '<User(IDUser={}, Login={}, is_admin={}>'.format(self.IDUser, self.Login, self.is_admin)

    # _table = 'users'
    # _entity_name = 'Пользователь'
    # _primary_key = 'IDUser'
    # # NOTE в данной версии предусмотрено всего лишь одно уникальное поле
    # # (для тестирования доп.функций)
    # _unique_field = 'Login'
    # _fields = {
    #     'Login': RequiredField(),
    #     'Password': RequiredField(),
    #     'is_admin': False
    # }
    # class ValidateSchema(mm.Schema):
    #     """Схема валидации модели."""
    #     Login = mm.fields.String(required=True)
    #     Password = mm.fields.String(required=True)
    #     is_admin = mm.fields.Boolean(required=True)

    # def sign_in(self, login, password):
    #     """Вход в программу"""
    #     stmt = sql.SQL('SELECT * FROM {} WHERE {}={}').format(
    #         sql.Identifier(self._table),
    #         sql.Identifier('Login'),
    #         sql.Literal(login)
    #     )
    #     row = self.execute_get_one(stmt)
    #     if not row:
    #         return {'!error': f'Пользователя с логином "{login}" не существует'}
    #     if row['Password'] != self.encrypt(password):
    #         return {'!error': f'Введенный пароль не совпадает'}

    #     return {'is_admin': row['is_admin']}

    # def create(self, **input_fields):
    #     """Добавление нового пользователя"""
    #     # проверка вставки дубликата уникальных имен
    #     if self.select_by_field('Login', input_fields['Login']):
    #         return {'!error': f'''Пользователь с логином "{input_fields['Login']}" уже существует'''}
    #     return super().create(**input_fields)

    # def is_unique(self, index, login):
    #     """Проверка уникальности поля (Login)"""
    #     user = self.select_by_field('Login', login)
    #     if not user or user[0][self._primary_key] == index:
    #         return True
    #     return False


class Material(db.Model, OperationMixin):
    """Модель материала здания"""
    __tablename__ = 'materials'
    _icase_unique_fields = ('Material',)

    IDMaterial = db.Column(db.Integer, primary_key=True)
    Material = db.Column(db.String(60), nullable=False, unique=True)


class Target(db.Model, OperationMixin):
    """Модель назначения помещения"""
    __tablename__ = 'targets'
    _icase_unique_fields = ('Target',)

    IDTarget = db.Column(db.Integer, primary_key=True)
    Target = db.Column(db.String(60), nullable=False, unique=True)
    # NOTE collation='NOCASE' не используется для UTF-8
    # Target = db.Column(db.String(60, collation='NOCASE'), nullable=False, unique=True)


class Department(db.Model, OperationMixin):
    """Модель кафедры"""
    __tablename__ = 'departments'

    IDDepartment = db.Column(db.Integer, primary_key=True)
    DepartmentName = db.Column(db.String(60), nullable=False)
    Boss = db.Column(db.String(60), nullable=False)
    Phone = db.Column(db.BigInteger, nullable=False)
    OfficeDean = db.Column(db.String(60), nullable=False)


class Building(db.Model, OperationMixin):
    """Модель здания"""
    __tablename__ = 'buildings'

    IDKadastr = db.Column(db.Integer, primary_key=True)
    BuildingName = db.Column(db.String(60))
    Land = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    Address = db.Column(db.String(250), nullable=False)
    Year = db.Column(db.SmallInteger, nullable=False)
    Wear = db.Column(db.SmallInteger, nullable=False)
    Flow = db.Column(db.SmallInteger, nullable=False)
    Picture = db.Column(db.String(250))
    Comment = db.Column(db.Text)
    MaterialID = db.Column(
        db.Integer,
        db.ForeignKey(
            'materials.IDMaterial',
            ondelete='SET NULL',
            onupdate='CASCADE',
        ),
        default=None,
    )
    Material = db.relationship('Material', uselist=False)


class Hall(db.Model, OperationMixin):
    """Модель помещения"""
    __tablename__ = 'halls'

    IDHall = db.Column(db.Integer, primary_key=True)
    HallNumber = db.Column(db.SmallInteger)
    # HallName = db.Column(db.String(60))
    HallSquare = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    Windows = db.Column(db.SmallInteger, nullable=False)
    Heaters = db.Column(db.SmallInteger, nullable=False)
    TargetID = db.Column(
        db.Integer,
        db.ForeignKey(
            'targets.IDTarget',
            ondelete='SET NULL',
            onupdate='CASCADE',
        ),
        default=None,
    )
    Target = db.relationship('Target', uselist=False)
    DepartmentID = db.Column(
        db.Integer,
        db.ForeignKey(
            'departments.IDDepartment',
            ondelete='SET NULL',
            onupdate='CASCADE',
        ),
        default=None,
    )
    Department = db.relationship('Department', uselist=False)
    KadastrID = db.Column(
        db.Integer,
        db.ForeignKey(
            'buildings.IDKadastr',
            ondelete='CASCADE',
            onupdate='CASCADE',
        ),
        nullable=False,
    )
    Building = db.relationship('Building', uselist=False)

    # _table = 'halls'
    # _entity_name = 'Помещение'
    # _primary_key = 'IDHall'
    # _fields = {
    #     'HallNumber': RequiredField(),
    #     'HallSquare': RequiredField(),
    #     'Windows': RequiredField(),
    #     'Heaters': RequiredField(),
    #     'TargetID': backref(TargetModel),
    #     'DepartmentID': backref(DepartmentModel),
    #     'KadastrID': backref(BuildingModel),
    #     'HallName': ComposedProperty(
    #         # из какой таблицы брать
    #         _table,
    #         {
    #             # название свойства, с которым оно будет возвращаться из БД
    #             'title': 'HallName',
    #             # объединяемые поля в псоледовательности объединения
    #             'fields': ('HallNumber', 'targets.Target', 'buildings.BuildingName'),# 'HouseNumber'),
    #             # разделитель полей при объединении (по умолчанию - пробел)
    #             'sep': ', ',
    #         }
    #     ),
    # }
    # class ValidateSchema(mm.Schema):
    #     """Схема валидации модели."""
    #     HallNumber = mm.fields.Integer(required=True, validate=mmv.Range(min=0))
    #     HallSquare = mm.fields.Float(required=True)
    #     Windows = mm.fields.Integer(required=True, validate=mmv.Range(min=0))
    #     Heaters = mm.fields.Integer(required=True, validate=mmv.Range(min=0))

    #     class Meta:
    #         unknown = mm.EXCLUDE


# class ChiefModel(BaseModel):
#     """Модель ответственного"""
#     _table = 'chiefs'
#     _entity_name = 'Ответственный'
#     _primary_key = 'IDChief'
#     _fields = {
#         'Chief': RequiredField(),
#         'AddressChief': RequiredField(),
#         'Experience': RequiredField(),
#     }
#     class ValidateSchema(mm.Schema):
#         """Схема валидации модели."""
#         Chief = mm.fields.String(required=True)
#         AddressChief = mm.fields.String(required=True)
#         Experience = mm.fields.Integer(required=True, validate=mmv.Range(min=0))


# class UnitModel(BaseModel):
#     """Модель имущества"""
#     _table = 'units'
#     _entity_name = 'Имущество'
#     _primary_key = 'IDUnit'
#     _fields = {
#         'UnitName': RequiredField(),
#         'DateStart': RequiredField(),
#         'Cost': RequiredField(),
#         'CostYear': RequiredField(),
#         'CostAfter': RequiredField(),
#         'Period': RequiredField(),
#         'HallID': backref(HallModel),
#         'ChiefID': backref(ChiefModel),
#     }
#     class ValidateSchema(mm.Schema):
#         """Схема валидации модели."""
#         UnitName = mm.fields.String(required=True)
#         DateStart = mm.fields.Date(required=True)
#         Cost = mm.fields.Float(required=True)
#         CostYear = mm.fields.Integer(required=True, validate=mmv.Range(min=1600, max=dt.datetime.now().year))
#         CostAfter = mm.fields.Float(required=True)
#         Period = mm.fields.Integer(required=True, validate=mmv.Range(min=0))

#         class Meta:
#             unknown = mm.EXCLUDE


if __name__ == '__main__':
    # NOTE доп.атрибуты: _sa_registry, metadata, query, query_class, registry
    print(dir(db.Model))
