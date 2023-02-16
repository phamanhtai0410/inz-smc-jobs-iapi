import pydash as py_
from pymodm import fields

from lib.enums.database import DBName
from lib.model import BaseMG
from lib.utils import dt_utcnow


class UserModel(BaseMG):
    class Meta:
        collection_name = 'users'
        final = True
        ignore_unknown_fields = True
        connection_alias = DBName.DAPP

    _id = fields.ObjectIdField(primary_key=True)
    last_login = fields.DateTimeField(default=dt_utcnow)
    username = fields.CharField(blank=True, default='Unnamed')
    avatar = fields.CharField(blank=True, default='')
    language = fields.CharField(blank=True, default='')
    password = fields.CharField(blank=True, default='')
    auth_username = fields.CharField(blank=True, default='')
    public_address = fields.CharField(blank=True, default='')