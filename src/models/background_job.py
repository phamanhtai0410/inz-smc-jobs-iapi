import pydash as py_
from pymodm import fields

from lib.enums.database import DBName
from lib.model import BaseMG


class BackgroundJobModel(BaseMG):
    class Meta:
        collection_name = 'background_jobs'
        final = True
        ignore_unknown_fields = True
        connection_alias = DBName.DAPP

    type = fields.CharField(required=True)
    contract = fields.CharField(required=True)
    # kwargs = fields.DictField(default={}, blank=True)

    task = fields.CharField()
    event = fields.CharField()

    interval = fields.CharField()
    task_id = fields.CharField()
    active = fields.BooleanField(default=False, blank=True)
    chain = fields.CharField()
    abi = fields.ListField(default=[], blank=True)
    from_block = fields.IntegerField(default=0, blank=True)
    start_at = fields.DateTimeField(default=None, blank=True)
    end_at = fields.DateTimeField(default=None, blank=True)
    auto_remove_at = fields.FloatField(default=0, blank=True)
