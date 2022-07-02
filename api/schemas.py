import datetime as dt
from marshmallow import Schema, fields, validate, post_load
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

from .models import (
    db,
    Building,
    Chief,
    Department,
    Hall,
    Material,
    Target,
    Unit,
    User,
)


# class BaseSchema(Schema):
#     __model__ = None

#     class Meta:
#         ordered = True

#     @post_load
#     def make_entity(self, data, **kwargs):
#         if self.__model__ is None:
#             return data
#         return self.__model__(**data)

class BaseSchema(SQLAlchemySchema):
    class Meta:
        sqla_session = db.session
        load_instance = True
        ordered = True

    @property
    def model(self):
        return self.opts.model

    @post_load
    def make_instance(self, data, **kwargs):
        # аргумент raw_dict_return используется разово
        if self.context.pop('raw_dict_return', None):
            return data
        return super().make_instance(data, **kwargs).encrypting()


class UserSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = User

    IDUser = auto_field(dump_only=True, data_key='id')
    Login = auto_field(
        required=True,
        validate=validate.Length(min=3, max=32),
        data_key='login',
    )
    Password = auto_field(
        required=True,
        validate=validate.Length(min=4, max=40),
        load_only=True,
        data_key='password'
    )
    is_admin = auto_field(
        load_default=False,
        data_key='admin'
    )

    # url = 


class TargetSchema(BaseSchema):
    IDTarget = auto_field(dump_only=True, data_key='id')
    Target = auto_field(
        required=True,
        validate=validate.Length(1),
        data_key='target'
    )

    class Meta(BaseSchema.Meta):
        model = Target


class MaterialSchema(BaseSchema):
    IDMaterial = auto_field(dump_only=True, data_key='id')
    Material = auto_field(
        required=True,
        validate=validate.Length(1),
        data_key='material'
    )

    class Meta(BaseSchema.Meta):
        model = Material


class DepartmentSchema(BaseSchema):
    IDDepartment = auto_field(dump_only=True, data_key='id')
    DepartmentName = auto_field(
        required=True,
        validate=validate.Length(1),
        data_key='department',
    )
    Boss = auto_field(
        required=True,
        validate=validate.Length(3),
        data_key='boss',
    )
    Phone = auto_field(
        required=True,
        data_key='phone',
    )
    OfficeDean = auto_field(
        required=True,
        validate=validate.Length(1),
        data_key='dienery',
    )

    class Meta(BaseSchema.Meta):
        model = Department


class BuildingSchema(BaseSchema):
    IDKadastr = auto_field(dump_only=True, data_key='id')
    BuildingName = auto_field(
        required=True,
        validate=validate.Length(min=1, max=60),
        data_key='building',
    )
    Land = fields.Float(
        required=True,
        validate=validate.Range(min=0.0),
        data_key='land',
    )
    Address = auto_field(
        required=True,
        validate=validate.Length(min=1, max=250),
        data_key='address',
    )
    Year = auto_field(
        required=True,
        validate=validate.Range(
            min=1600,
            max=dt.date.today().year,
        ),
        data_key='year',
    )
    Wear = auto_field(
        required=True,
        validate=validate.Range(min=0, max=100),
        data_key='wear',
    )
    Flow = auto_field(
        required=True,
        validate=validate.Range(min=1, max=100),
        data_key='flow',
    )
    Picture = auto_field(
        allow_none=True,
        load_default=None,
        validate=validate.Length(max=250),
    )
    Comment = auto_field(allow_none=True, load_default=None)
    # MaterialID = fields.Nested(
    #     MaterialSchema(only=('Material',)),
    #     required=True,
    #     # only=('Material',)
    #     data_key='material',
    # )
    MaterialID = auto_field(
        required=True,
        allow_none=True,
        validate=validate.Range(min=1),
        data_key='material_id',
    )
    # Nested - будет весь словарь данных Material
    # Pluck - только одно, выбранное значение
    Material = fields.Pluck(
        MaterialSchema,
        'Material',
        dump_only=True,
        data_key='material',
    )

    class Meta(BaseSchema.Meta):
        model = Building
        include_fk = True
        include_relationships = True


class HallSchema(BaseSchema):
    IDHall = auto_field(dump_only=True, data_key='id')
    HallNumber = auto_field(
        required=True,
        allow_none=True,
        validate=validate.Range(min=1),
        data_key='number',
    )
    HallSquare = fields.Float(
        required=True,
        validate=validate.Range(min=0.0),
        data_key='square',
    )
    Windows = auto_field(
        required=True,
        validate=validate.Range(min=0),
        data_key='windows',
    )
    Heaters = auto_field(
        required=True,
        validate=validate.Range(min=0),
        data_key='heaters',
    )
    TargetID = auto_field(
        required=True,
        allow_none=True,
        validate=validate.Range(min=1),
        data_key='target_id',
    )
    Target = fields.Pluck(
        TargetSchema,
        'Target',
        dump_only=True,
        data_key='target',
    )
    DepartmentID = auto_field(
        required=True,
        allow_nonw=True,
        validate=validate.Range(min=1),
        data_key='department_id',
        # attribute='IDDepartment',
    )
    Department = fields.Pluck(
        DepartmentSchema,
        'DepartmentName',
        dump_only=True,
        data_key='department',
    )
    KadastrID = auto_field(
        required=True,
        validate=validate.Range(min=1),
        data_key='building_id',
    )
    Building = fields.Pluck(
        BuildingSchema,
        'BuildingName',
        dump_only=True,
        data_key='building',
    )

    class Meta(BaseSchema.Meta):
        model = Hall
        include_fk = True
        include_relationships = True


class ChiefSchema(BaseSchema):
    IDChief = auto_field(dump_only=True, data_key='id')
    Chief = auto_field(
        required=True,
        validate=validate.Length(min=1, max=60),
        data_key='chief',
    )
    AddressChief = auto_field(
        required=True,
        validate=validate.Length(min=3, max=120),
        data_key='address_chief',
    )
    Experience = auto_field(
        required=True,
        validate=validate.Range(min=0),
        data_key='experience'
    )

    class Meta(BaseSchema.Meta):
        model = Chief


class UnitSchema(BaseSchema):
    IDUnit = auto_field(dump_only=True, data_key='id')
    UnitName = auto_field(
        required=True,
        validate=validate.Length(min=1, max=60),
        data_key='unit',
    )
    DateStart = auto_field(
        required=True,
        validate=validate.Range(max=dt.date.today()),
        data_key='date_start',
    )
    Cost = fields.Float(
        required=True,
        validate=validate.Range(min=0.0),
        data_key='cost'
    )
    CostYear = auto_field(
        required=True,
        allow_none=True,
        validate=validate.Range(
            min=1600,
            max=dt.date.today().year,
        ),
        data_key='cost_year'
    )
    CostAfter = fields.Float(
        required=True,
        allow_none=True,
        validate=validate.Range(min=0.0),
        data_key='cost_after'
    )
    Period = auto_field(
        required=True,
        validate=validate.Range(min=0),
        data_key='period'
    )
    ChiefID = auto_field(
        required=True,
        allow_none=True,
        validate=validate.Range(min=1),
        data_key='chief_id',
    )
    Chief = fields.Pluck(
        ChiefSchema,
        'Chief',
        dump_only=True,
        data_key='chief',
    )
    HallID = auto_field(
        required=True,
        allow_none=True,
        validate=validate.Range(min=1),
        data_key='hall_id',
    )
    HallTitle = fields.Method(
        'get_hall_title',
        dump_only=True,
        data_key='hall',
    )

    def get_hall_title(self, unit):
        """."""
        hall = unit.Hall
        title = ''
        if hall.HallNumber is not None:
            title += f'{hall.HallNumber}'
        if (target := hall.Target.Target) is not None:
            title += '{}{}'.format(
                f', ' if title else '',
                target
            )
        return title if title else 'Не определено'

    class Meta(BaseSchema.Meta):
        model = Unit


user_schema = UserSchema()
target_schema = TargetSchema()
material_schema = MaterialSchema()
department_schema = DepartmentSchema()
building_schema = BuildingSchema()
hall_schema = HallSchema()
chief_schema = ChiefSchema()
unit_schema = UnitSchema()

json_schemas = {
    'user': UserSchema(),
    'target': TargetSchema(),
    'material': MaterialSchema(),
    'department': DepartmentSchema(),
    'building': BuildingSchema(),
    'hall': HallSchema(),
    'chief': ChiefSchema(),
    'unit': UnitSchema(),
}