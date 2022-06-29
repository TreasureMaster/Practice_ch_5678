import datetime as dt

from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect
# import marshmallow as mm
# import marshmallow.validate as mmv


db = SQLAlchemy()


class OperationMixin:
    # список полей, которые нужно шифровать перед записью в БД
    _secret_fields = ()

    def _add(self):
        db.session.add(self)
        db.session.commit()

    def create(self):
        self._add()

    def update(self, patched_fields):
        self.patch_fields(patched_fields)
        self._add()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def patch_fields(self, patched_fields):
        for field, value in patched_fields.items():
            setattr(self, field, value)

    def encrypting(self):
        """Шифрование полей, которые должны быть зашифрованы перед помещением в БД"""
        for field in self._secret_fields:
            if getattr(self, field, None) is not None:
                setattr(self, field, generate_password_hash(getattr(self, field)))
        return self

    @classmethod
    def check_unique(cls, fields, pk=None):
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
                # (e := cls.query.filter(c == attr).first()) is not None
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
    def get_not_unique(cls, column, attr):
        """Возвращает первое попавшееся не уникальное поле для заданной колонки
        или None, если его нет.
        """
        return cls.query.filter(column == attr).first()

    # @classmethod
    # def get_last_item(cls):
    #     """Возвращает последнюю вставленную запись"""
    #     return cls.query.order_by(cls.get_primary().desc()).first()


class User(db.Model, OperationMixin):
    """Модель пользователя"""
    __tablename__ = 'users'
    _secret_fields = ('Password',)

    IDUser = db.Column(db.Integer, primary_key=True)
    Login = db.Column(db.String(32), nullable=False, unique=True)
    Password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
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

    IDMaterial = db.Column(db.Integer, primary_key=True)
    Material = db.Column(db.String(60), nullable=False, unique=True)
    # _table = 'materials'
    # _entity_name = 'Материал'
    # _primary_key = 'IDMaterial'
    # _unique_field = 'Material'
    # _fields = {
    #     'Material': RequiredField(),
    # }
    # class ValidateSchema(mm.Schema):
    #     """Схема валидации модели."""
    #     Material = mm.fields.String(required=True)


class Target(db.Model, OperationMixin):
    """Модель назначения помещения"""
    __tablename__ = 'targets'

    IDTarget = db.Column(db.Integer, primary_key=True)
    Target = db.Column(db.String(60), nullable=False, unique=True)
    # NOTE collation='NOCASE' не используется для UTF-8
    # Target = db.Column(db.String(60, collation='NOCASE'), nullable=False, unique=True)
    # _table = 'targets'
    # _entity_name = 'Тип помещения'
    # _primary_key = 'IDTarget'
    # _unique_field = 'Target'
    # _fields = {
    #     'Target': RequiredField(),
    # }
    # class ValidateSchema(mm.Schema):
    #     """Схема валидации модели."""
    #     Target = mm.fields.String(required=True)


class Department:
    """Модель кафедры"""
    __tablename__ = 'departments'

    IDDepartment = db.Column(db.Integer, primary_key=True)
    DepartmentName = db.Column(db.String(60), nullable=False)
    Phone = db.Column(db.BigInteger, nullable=False)
    OfficeDean = db.Column(db.String(60), nullable=False)

    # _table = 'departments'
    # _entity_name = 'Кафедра'
    # _primary_key = 'IDDepartment'
    # _fields = {
    #     'DepartmentName': RequiredField(),
    #     'Boss': RequiredField(),
    #     'Phone': RequiredField(),
    #     'OfficeDean': RequiredField(),
    # }
    # class ValidateSchema(mm.Schema):
    #     """Схема валидации модели."""
    #     DepartmentName = mm.fields.String(required=True)
    #     Boss = mm.fields.String(required=True)
    #     Phone = mm.fields.Integer(required=True)
    #     OfficeDean = mm.fields.String(required=True)


class Building:
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
        db.ForeignKey('materials.IDMaterial'),
        nullable=False
    )
    Material = db.relationship('Material', cascade='all, delete')
    # Wear = db.Column(db.)
    # _table = 'buildings'
    # _entity_name = 'Здание'
    # _primary_key = 'IDKadastr'
    # _fields = {
    #     'BuildingName': RequiredField(),
    #     'Land': RequiredField(),
    #     'Address': RequiredField(),
    #     'Year': RequiredField(),
    #     'Wear': RequiredField(),
    #     'Flow': RequiredField(),
    #     'Picture': None,
    #     'Comment': None,
    #     'MaterialID': backref(MaterialModel),
    # }
    # class ValidateSchema(mm.Schema):
    #     """Схема валидации модели."""
    #     BuildingName = mm.fields.String(required=True)
    #     Land = mm.fields.Float(required=True)
    #     Address = mm.fields.String(required=True)
    #     Year = mm.fields.Integer(required=True, validate=mmv.Range(min=1600, max=dt.datetime.now().year))
    #     Wear = mm.fields.Integer(required=True, validate=mmv.Range(min=0, max=100))
    #     Flow = mm.fields.Integer(required=True, validate=mmv.Range(min=1, max=100))
    #     Picture = mm.fields.String(allow_none=True)
    #     Comment = mm.fields.String(allow_none=True)

    #     class Meta:
    #         unknown = mm.EXCLUDE


# class Hall:
#     """Модель помещения"""
#     __tablename__ = 'halls'

#     IDHall = db.Column(db.Integer, primary_key=True)
#     HallNumber = db.Column(db.SmallInteger, nullable=False)
#     HallSqaure = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
#     Windows = db.Column(db.SmallInteger, nullable=False)
#     Heaters = db.Column(db.SmallInteger, nullable=False)

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
