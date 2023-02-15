# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""

from pymodm import fields

from lib.enums.database import DBName
from lib.model import BaseMG


class SupplyNFTModel(BaseMG):
    """
        Define all NFT data of INZ Media NFTs will be stored
    """

    class Meta:
        collection_name = 'supply_nft'
        final = True
        connection_alias = DBName.DAPP

    _id = fields.ObjectIdField(primary_key=True)
    contract = fields.CharField(blank=True)
    type = fields.IntegerField(default=0, blank=True)
    total_supply = fields.IntegerField(default=0, blank=True)
