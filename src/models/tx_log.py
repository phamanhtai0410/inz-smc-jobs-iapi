# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
import pydash as py_
from pymodm import fields

from lib.enums.database import DBName
from lib.model import BaseMG
from lib.util import dt_utcnow


class TxLogModel(BaseMG):
    class Meta:
        collection_name = 'tx_logs'
        final = True
        ignore_unknown_fields = True
        connection_alias = DBName.DAPP

    _id = fields.ObjectIdField(primary_key=True)
    tx_type = fields.CharField()
    tx_hash = fields.CharField(default='')
    contract = fields.CharField()
    event = fields.DictField()
    block_number = fields.IntegerField()
    confirm = fields.BooleanField()

