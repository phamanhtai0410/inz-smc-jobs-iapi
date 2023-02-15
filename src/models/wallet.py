# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from bson import ObjectId
from pymodm import fields

from lib.enums.database import DBName
from lib.model import BaseMG
from src.models.user import UserModel


class WalletModel(BaseMG):
    class Meta:
        collection_name = 'wallets'
        final = True
        ignore_unknown_fields = True
        connection_alias = DBName.DAPP

    public_address = fields.CharField()
    user = fields.ObjectIdField()
    active = fields.BooleanField(default=True, blank=True)
    network = fields.CharField(default='', blank=True)

    @classmethod
    def user_of(cls, address: str, with_upsert=False):
        _wallet = cls.find_one(filter={
            'public_address': address
        })
        if _wallet:
            return UserModel.find_one(filter={
                '_id': _wallet['user']
            })
        elif with_upsert:
            _user = UserModel.insert({
                "public_address": address
            }).to_dict()
            cls.insert({
                'public_address': address,
                'user': _user['_id'],
                'active': True
            })
            return _user

        return {}

    @classmethod
    def wallet_of(cls, user: ObjectId):
        """
            - Get wallet of user
        """
        return cls.find_one(filter={
            'user': user
        })
