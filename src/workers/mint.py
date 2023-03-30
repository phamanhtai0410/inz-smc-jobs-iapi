# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
import json
import traceback
from time import sleep

import requests
import sentry_sdk
from bson import ObjectId
from pydash import get, find
from pymongo import ReturnDocument
from web3 import Web3

from lib.logger import LoggerTask
from lib.utils import dt_utcnow
from src.config import DefaultConfig
from src.enums.mint import MintStatus, AssetType
from src.extensions import bsc_web3, polygon_web3, ether_web3
from src.models.background_job import BackgroundJobModel
from src.models.dev_wallet import DevWalletModel
from src.models.mint_log import MintLogModel
from src.models.nft import NFTModel
from src.models.nft_contracts import NftContractModel
from src.models.supply import SupplyNFTModel
from src.models.tx_log import TxLogModel
from src.models.user import UserModel
from src.models.wallet import WalletModel
from src.worker import worker


@worker.task(name="worker.on_mint_nft", rate_limit='10000/s')
def on_mint_nft(event, chain_name="BSC"):
    try:
        LoggerTask.debug(event, chain_name)
        _tx_hash = get(event, 'transactionHash', '').lower()
        _contract = get(event, 'address').lower()
        _tx = TxLogModel.db().find_one_and_update(
            filter={
                'tx_hash': _tx_hash
            },
            update=[{
                '$set': {
                    'tx_type': "TokenCreated",
                    'contract': _contract,
                    'event': json.dumps(event),
                    'block_number': get(event, 'blockNumber'),
                    "updated_time": dt_utcnow(),
                    "created_time": {"$cond": [{"$not": ["$created_time"]}, dt_utcnow(), "$created_time"]},
                }
            }],
            upsert=True,
            return_document=ReturnDocument.BEFORE
        )
        if _tx:
            return f"Reject tx {_tx_hash}"
        _owner = get(event, 'args.to').lower()
        _token_id = get(event, 'args.tokenId')
        _upsert = True
        _active_code = False
        _asset = ''
        _index_type = get(event, 'args.tokenType')

        _update = {
            "on_market": False,
            "mint_status": MintStatus.MINTED,
            'type': _index_type,
            'updated_time': dt_utcnow(),
            "created_time": {"$cond": [{"$not": ["$created_time"]}, dt_utcnow(), "$created_time"]}
        }

        _is_dev = DevWalletModel.find_one(filter={
            'public_address': _owner
        }, with_cache=False)
        _user_id = None

        if not _is_dev:

            _wallet_owner = WalletModel.find_one(filter={
                'public_address': _owner
            }, with_cache=False)

            if not _wallet_owner:
                _user = UserModel.insert({
                    "public_address": _owner
                })
                _user_id = _user._id
                WalletModel.insert({
                    'public_address': _owner,
                    'user': _user_id,
                    'active': True
                })
            else:
                _user_id = _wallet_owner['user'] if isinstance(_wallet_owner['user'], ObjectId) else ObjectId(
                    _wallet_owner['user'])

            _update['user'] = _user_id
        else:
            _update['keep'] = True

        if _active_code:
            if _asset:
                _mint_log = MintLogModel.find_one({'mark': _active_code})
                if not _mint_log:
                    sentry_sdk.capture_message(f"Not found owner of log - mark={_active_code}")
                else:
                    _update['user'] = _mint_log['user']

        _filter = {
            'contract': _contract,
            'token_id': _token_id
        }

        _bf = NFTModel.db().find_one_and_update(filter=_filter, update=[{
            "$set": _update
        }], upsert=True, return_document=ReturnDocument.BEFORE)

        try:
            if not _bf:
                SupplyNFTModel.db().find_one_and_update(filter={
                    'contract': _contract,
                    'type': _index_type
                }, update={
                    '$inc': {
                        'total_supply': 1
                    }
                }, upsert=True)
        except:
            sentry_sdk.capture_exception()
            traceback.print_exc()
            
        # Init metadata link
        _contract_detail = NftContractModel.find_one({
            'contract': _contract
        }, with_cache=False)
        if not _contract_detail:
            raise Exception(f'Not found nft contract of address {_contract}')
        _type = find(get(_contract_detail, 'nft_list'), lambda x: get(x, 'index_type') == _index_type)
        if not _type:
            raise Exception(f"Not found type of {_type}")

        _metadata = {
            'name': get(_type, 'name', ''),
            'image_url': get(_type, 'image_url', ''),
            'description': get(_type, 'description', ''),
            'type': get(_type, 'type'),
            'attributes': get(_type, 'properties', []),
            'actions': get(_type, 'actions', []),
        }

        _data = {
            'contract': _contract,
            'token_id': _token_id,
            'metadata': _metadata
        }

        _response = requests.post(f'{DefaultConfig.IAPI_STORAGE_URI}/metadata', json=_data, timeout=30)
        LoggerTask.debug(f'_response from metadata {_response.text}')
        if _response.status_code != 200:
            raise Exception(f'Create metadata error {_response.text}')
        
        return 'done'

    except:
        sentry_sdk.capture_exception()
        traceback.print_exc()
        return "Fail"
