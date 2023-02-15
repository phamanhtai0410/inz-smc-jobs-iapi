# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""

from pymodm import fields

from lib.enums.database import DBName
from lib.model import BaseMG


class DevWalletModel(BaseMG):
    """
        Define all NFT data of INZ Media NFTs will be stored
    """

    class Meta:
        collection_name = 'dev_wallet'
        final = True
        connection_alias = DBName.DAPP

    _id = fields.ObjectIdField(primary_key=True)
    public_address = fields.CharField(blank=True)
