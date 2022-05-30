from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    IDUser = fields.Integer(dump_only=True, data_key='id')
    Login = fields.String(required=True, data_key='login')
    Password = fields.String(required=True, validate=validate.Length(3), load_only=True, data_key='password')
    is_admin = fields.Boolean(required=True, data_key='admin')
    # url = 

    class Meta:
        ordered = True


user_schema = UserSchema()