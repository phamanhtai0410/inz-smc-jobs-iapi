
from pymodm import fields
from lib.enums.database import DBName
from lib.model import BaseMG
from lib.utils import dt_utcnow


class NftContractModel(BaseMG):
    class Meta:
        collection_name = 'nft_contracts'
        final = True
        ignore_unknown_fields = True
        connection_alias = DBName.DAPP

    # auto-gen id field
    _id = fields.ObjectIdField(primary_key=True)

    # Info for creation form
    name = fields.CharField(blank=True, default='Unnamed')
    image_url = fields.CharField(blank=True, default='')
    highlight_text = fields.CharField(blank=True, default='')
    symbol = fields.CharField(blank=True, default='')
    chain = fields.CharField(blank=True, default='BSC')
    currency = fields.CharField(blank=True, default='BUSD')
    website_domain = fields.CharField(blank=True, default='')
    social_link = fields.DictField(blank=True, default={})
    # campaign_method = fields.IntegerField(blank=True, default=1)
    nft_list = fields.ListField(blank=True, default=[])

    # implicit fields
    user = fields.CharField(blank=True, default='')
    contract = fields.CharField(blank=True, default='')
    deploy_address = fields.CharField(blank=True, default='')
    is_released = fields.BooleanField(blank=False, default=False)
    
    # campaign desciption
    description = fields.CharField(blank=True, default='')