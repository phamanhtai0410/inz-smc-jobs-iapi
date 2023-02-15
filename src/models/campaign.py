
from pymodm import fields
from lib.enums.database import DBName
from lib.model import BaseMG
from lib.util import dt_utcnow


class CampaignModel(BaseMG):
    class Meta:
        collection_name = 'campaign'
        final = True
        ignore_unknown_fields = True
        connection_alias = DBName.DAPP

    # auto-gen id field
    _id = fields.ObjectIdField(primary_key=True)

    # Info for creation form
    name = fields.CharField(blank=True, default='Unnamed')
    image_url = fields.CharField(blank=True, default='')
    highlight_text = fields.CharField(blank=True, default='')
    max_allocation = fields.IntegerField(blank=True, default=None)
    allocation_symbol = fields.CharField(blank=True, default='')
    chain_name = fields.CharField(blank=True, default='BSC')
    chain_currency = fields.CharField(blank=True, default='BNB')
    total_supply = fields.IntegerField(blank=True, default=1) 
    total_raise = fields.IntegerField(blank=True, default=1)
    start_time = fields.DateTimeField(blank=True)
    end_time = fields.DateTimeField(blank=True)
    website_domain = fields.CharField(blank=True, default='')
    social_link = fields.DictField(blank=True, default={})
    campaign_method = fields.IntegerField(blank=True, default=1)
    random_nft = fields.BooleanField(blank=True, default=False)
    nft_list = fields.ListField(blank=True, default=[])

    # implicit fields
    user = fields.CharField(blank=True, default='')
    contract = fields.CharField(blank=True, default='')
    deploy_address = fields.CharField(blank=True, default='')
    is_fixed_token = fields.BooleanField(blank=True, default=False)
    is_released = fields.BooleanField(blank=False, default=False)
    
    # campaign desciption
    description = fields.CharField(blank=True, default='')
    about_kol = fields.CharField(blank=True, default='')
    kol_image_url = fields.CharField(blank=True, default='')