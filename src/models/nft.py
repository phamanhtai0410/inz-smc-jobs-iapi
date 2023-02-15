# -*- coding: utf-8 -*-


# File: report.py
# Created at 16/11/2021
"""
   Description:
        -
        -This model saved infos of NFTs
"""

from pymodm import fields

from lib.enums.database import DBName
from lib.enums.tx_status import TxOffChainStatus
from lib.model import BaseMG


class NFTModel(BaseMG):
    """
        Define all NFT data of INZ Media NFTs will be stored
    """

    class Meta:
        collection_name = 'nft'
        final = True
        connection_alias = DBName.DAPP

    _id = fields.ObjectIdField(primary_key=True)

    public_address = fields.CharField(blank=True)
    metadata_link = fields.CharField(blank=True)
    type = fields.IntegerField(default=0, blank=True)
    user = fields.ObjectIdField(blank=True)

    miner = fields.ObjectIdField(blank=True)

    contract = fields.CharField()
    token_id = fields.IntegerField(blank=True)

    # If nft keep by dev wallet
    keep = fields.BooleanField(default=False, blank=True)
    on_market = fields.BooleanField(default=False, blank=True)
    price = fields.FloatField(default=0, blank=False)
    # MINTED, BURN, MINT_PROCESS
    mint_status = fields.CharField(default='', blank=True)
    status = fields.CharField(default=TxOffChainStatus.PENDING, blank=True)
    active_code = fields.CharField(blank=True)
