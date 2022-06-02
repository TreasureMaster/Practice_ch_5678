import datetime as dt
from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    IDUser = fields.Integer(dump_only=True, data_key='id')
    Login = fields.String(
        required=True,
        validate=validate.Length(3),
        data_key='login'
    )
    Password = fields.String(
        required=True,
        validate=validate.Length(min=4, max=32),
        load_only=True,
        data_key='password'
    )
    is_admin = fields.Boolean(required=True, data_key='admin')
    # url = 

    class Meta:
        ordered = True


class TargetSchema(Schema):
    IDTarget = fields.Integer(dump_only=True, data_key='id')
    Target = fields.String(
        required=True,
        validate=validate.Length(1),
        data_key='target'
    )

    class Meta:
        ordered = True


class MaterialSchema(Schema):
    IDMaterial = fields.Integer(dump_only=True, data_key='id')
    Material = fields.String(
        required=True,
        validate=validate.Length(1),
        data_key='material'
    )

    class Meta:
        ordered = True


class DepartmentSchema(Schema):
    IDDepartment = fields.Integer(dump_only=True, data_key='id')
    DepartmentName = fields.String(
        required=True,
        validate=validate.Length(1),
        data_key='department',
    )
    Boss = fields.String(
        required=True,
        validate=validate.Length(3),
        data_key='boss',
    )
    Phone = fields.Integer(
        required=True,
        data_key='phone',
    )
    OfficeDean = fields.String(
        required=True,
        validate=validate.Length(1),
        data_key='dienery',
    )

    class Meta:
        ordered = True


class BuildingSchema(Schema):
    IDKadastr = fields.Integer(dump_only=True, data_key='id')
    BuildingName = fields.String(
        required=True,
        validate=validate.Length(1),
        data_key='building',
    )
    Land = fields.Float(
        required=True,
        validate=validate.Range(min=0.0),
        data_key='land',
    )
    Address = fields.String(
        required=True,
        validate=validate.Length(1),
        data_key='address',
    )
    Year = fields.Integer(
        required=True,
        validate=validate.Range(
            min=1600,
            max=dt.date.today().year,
        ),
        data_key='year',
    )
    Wear = fields.Integer(
        required=True,
        validate=validate.Range(min=0, max=100),
        data_key='wear',
    )
    Flow = fields.Integer(
        required=True,
        validate=validate.Range(min=1, max=100),
        data_key='flow',
    )
    Picture = fields.String(allow_none=True, load_default=None)
    Comment = fields.String(allow_none=True, load_default=None)
    # MaterialID = fields.Nested(
    #     MaterialSchema(only=('Material',)),
    #     required=True,
    #     # only=('Material',)
    #     data_key='material',
    # )
    # Эта схема работы только для своей ОРМ; для SQLAlchemy нужно будет переделать
    MaterialID = fields.Integer(
        required=True,
        validate=validate.Range(min=1),
        data_key='material_id',
    )
    Material = fields.String(
        required=True,
        dump_only=True,
        data_key='material',
    )

    class Meta:
        ordered = True


class HallSchema(Schema):
    IDHall = fields.Integer(dump_only=True, data_key='id')
    HallNumber = fields.Integer(
        required=True,
        validate=validate.Range(min=0),
        data_key='number',
    )
    HallSquare = fields.Float(
        required=True,
        validate=validate.Range(min=0.0),
        data_key='square',
    )
    Windows = fields.Integer(
        required=True,
        validate=validate.Range(min=0),
        data_key='windows',
    )
    Heaters = fields.Integer(
        required=True,
        validate=validate.Range(min=0),
        data_key='heaters',
    )
    TargetID = fields.Integer(
        required=True,
        validate=validate.Range(min=1),
        data_key='target_id',
    )
    Target = fields.String(
        required=True,
        dump_only=True,
        data_key='target',
    )
    DepartmentID = fields.Integer(
        required=True,
        validate=validate.Range(min=1),
        data_key='department_id',
        # attribute='IDDepartment',
    )
    DepartmentName = fields.String(
        required=True,
        dump_only=True,
        data_key='department',
    )
    KadastrID = fields.Integer(
        required=True,
        validate=validate.Range(min=1),
        data_key='building_id',
    )
    BuildingName = fields.String(
        required=True,
        dump_only=True,
        data_key='building',
    )
    HallName = fields.String(
        required=True,
        dump_only=True,
        data_key='hall',
    )

    class Meta:
        ordered = True


class ChiefSchema(Schema):
    IDChief = fields.Integer(dump_only=True, data_key='id')
    Chief = fields.String(
        required=True,
        validate=validate.Length(1),
        data_key='chief',
    )
    AddressChief = fields.String(
        required=True,
        validate=validate.Length(3),
        data_key='address_chief',
    )
    Experience = fields.Integer(
        required=True,
        validate=validate.Range(min=0),
        data_key='experience'
    )

    class Meta:
        ordered = True


class UnitSchema(Schema):
    IDUnit = fields.Integer(dump_only=True, data_key='id')
    UnitName = fields.String(
        required=True,
        validate=validate.Length(1),
        data_key='unit',
    )
    DateStart = fields.Date(
        required=True,
        # validate=validate.Length(3),
        data_key='date_start',
    )
    Cost = fields.Float(
        required=True,
        validate=validate.Range(min=0),
        data_key='cost'
    )
    CostYear = fields.Integer(
        required=True,
        validate=validate.Range(
            min=1600,
            max=dt.date.today().year,
        ),
        data_key='cost_year'
    )
    CostAfter = fields.Float(
        required=True,
        validate=validate.Range(min=0),
        data_key='cost_after'
    )
    Period = fields.Integer(
        required=True,
        validate=validate.Range(min=0),
        data_key='period'
    )
    ChiefID = fields.Integer(
        required=True,
        validate=validate.Range(min=1),
        data_key='chief_id',
    )
    Chief = fields.String(
        required=True,
        dump_only=True,
        data_key='chief',
    )
    HallID = fields.Integer(
        required=True,
        validate=validate.Range(min=1),
        data_key='hall_id',
    )
    HallName = fields.String(
        required=True,
        dump_only=True,
        data_key='hall',
    )

    class Meta:
        ordered = True


user_schema = UserSchema()
target_schema = TargetSchema()
material_schema = MaterialSchema()
department_schema = DepartmentSchema()
building_schema = BuildingSchema()
hall_schema = HallSchema()
chief_schema = ChiefSchema()
unit_schema = UnitSchema()