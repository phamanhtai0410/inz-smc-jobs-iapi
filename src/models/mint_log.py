# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from pymodm import fields

from lib.enums.database import DBName
from lib.model import BaseMG


class MintLogModel(BaseMG):
    class Meta:
        collection_name = 'miner_logs'
        final = True
        ignore_unknown_fields = True
        connection_alias = DBName.DAPP

    type = fields.CharField(blank=True)
    tx_hash = fields.CharField(blank=True)
    chain = fields.CharField(blank=True)
    status = fields.CharField(blank=True)
    msg = fields.CharField(blank=True)
    origin_id = fields.ObjectIdField(blank=True)
    tx_info = fields.DictField(blank=True)
    user = fields.ObjectIdField(blank=True)
    mark = fields.CharField(default='', blank=True)
