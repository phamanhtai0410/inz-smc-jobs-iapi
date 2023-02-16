# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""

import json
import sys
import time
import traceback
from datetime import datetime, timezone
from time import sleep

from bson import ObjectId
from pymodm import connect


sys.path.append(".")
from src.scripts.logger import LoggerTask

# from lib.logger import LoggerTask

# from lib.enums.database import DBName
# from lib.utils import dt_utcnow
from src.extensions import redis_cluster
import sentry_sdk
from hexbytes import HexBytes
from pydash import get
from web3.datastructures import AttributeDict
from web3.middleware import geth_poa_middleware
from src.models.background_job import BackgroundJobModel

import src.workers as workers
from src.helper import EventScannerState, EventScanner
from src.extensions import dlm
from src.util import make_red_key, remove_task
import pydash
from web3 import Web3

from src.config import DefaultConfig


class DBName:
    DAPP = 'inz-dapp'


def dt_utcnow():
    return datetime.utcnow().replace(tzinfo=timezone.utc)


connect(DefaultConfig.DB_DAPP, alias=DBName.DAPP, connect=False)


class Provider(object):

    def __init__(self, provider, *args, **kwargs):
        self.rpc = provider
        self.contract = None
        self.web3 = Web3(Web3.HTTPProvider(provider, *args, **kwargs))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    def set_contract(self, contract, abi):
        self.contract = self.web3.eth.contract(address=Web3.toChecksumAddress(contract), abi=abi)

    def set_handle(self, callback):
        self.callback = callback

    def init_contract(self, contract_address, abi_file):
        self.contract = self.web3.eth.contract(address=Web3.toChecksumAddress(contract_address), abi=abi_file)

    def get_event_func(self, event):
        return getattr(self.contract.events, event)

    def init_scanner(self, state, event):
        self.scanner = EventScanner(
            web3=self.web3,
            contract=self.contract,
            state=state,
            events=[event],
            filters={
                "address": self.contract.address
            },
            max_chunk_scan_size=5000
        )


#
#
# @handle_exception()
# def handle_log(event, wk_handle, provider):
#

class HexJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, HexBytes):
            return obj.hex()
        return super().default(obj)


class RedisState(EventScannerState):
    """Store the state of scanned blocks and all events.

    All state is an in-memory dict.
    Simple load/store massive JSON on start up.
    """

    def __init__(self, address, event, handle_log):
        self.state = None
        self.wk_handle = handle_log
        self.key_state = f'state_cron/scanner:{address.lower()}:{event}'
        self.last_save = 0
        self.address = address
        self.restore()

    def reset(self):
        """Create initial state of nothing scanned."""
        self.state = {
            "last_scanned_block": 0,
            "blocks": {},
        }

    def restore(self):
        """Restore the last scan state from a file."""
        try:
            _state = redis_cluster.get(self.key_state)
            if _state:
                self.state = json.loads(_state)
            else:
                self.reset()
            print(f"Restored the state, previously {self.state['last_scanned_block']} blocks have been scanned")
        except (IOError, json.decoder.JSONDecodeError):
            print("State starting from scratch")
            self.reset()

    def save(self):
        """Save everything we have scanned so far in a file."""
        _state = json.dumps(self.state)
        redis_cluster.set(self.key_state, _state)
        self.last_save = time.time()

    #
    # EventScannerState methods implemented below
    #

    def get_last_scanned_block(self):
        """The number of the last block we have stored."""
        return self.state["last_scanned_block"]

    def delete_data(self, since_block):
        """Remove potentially reorganised blocks from the scan data."""
        for block_num in range(since_block, self.get_last_scanned_block()):
            if block_num in self.state["blocks"]:
                del self.state["blocks"][block_num]

    def start_chunk(self, block_number, chunk_size):
        pass

    def end_chunk(self, block_number):
        """Save at the end of each block, so we can resume in the case of a crash or CTRL+C"""
        # Next time the scanner is started we will resume from this block
        self.state["last_scanned_block"] = block_number

        # Save the database file for every minute
        # if time.time() - self.last_save > 10:
        print(f"Save state {self.state}")

        self.save()

    def process_event(self, block_when: datetime, event: AttributeDict) -> dict:
        # raise Exception(f'{event}')
        try:
            _event = Web3.toJSON(event)

            _json = json.loads(_event)
            _json['transactionHash'] = _json['transactionHash'].lower()

            _tx_hash = pydash.get(_json, 'transactionHash')
            LoggerTask.debug(f'[LOG] event {_json}')
            if _tx_hash:
                _key = make_red_key(
                    tx_hash=_tx_hash,
                    contract=self.address.lower()
                )
                _lock = dlm.lock(_key, 60 * 5)
                LoggerTask.debug(f'[LOG]  🔑 🔑 🔑 Key lock: {_key}')
                if _lock:
                    LoggerTask.debug(f'[LOG] \033[92m ✔✔✔ Process .................. {_tx_hash} \033[0m')
                    self.wk_handle.delay(_json)
                else:
                    LoggerTask.debug(f'[LOG] \033[93m ⚠⚠⚠ ______ Lock fail ______ {_tx_hash} \033[0m')
        except:
            sentry_sdk.capture_exception()
            traceback.print_exc()
        return {
            "blockNumber": get(event, "blockNumber")
        }


# if __name__ == "__main__":
def run_logs(**kwargs):
    contract = kwargs['contract']
    INIT_BLOCK_NUMBER = kwargs['from_block']

    providers = getattr(DefaultConfig, f'{kwargs["chain"]}_RPC_URIS')
    auto_remove_at = get(kwargs, 'auto_remove_at', 0)
    event = kwargs['event']
    abi = kwargs['abi']
    handle_func = kwargs['task']

    _func = getattr(workers, handle_func)
    if isinstance(abi, str):
        with open(abi) as file:
            abi = json.load(file)

    if not _func:
        raise Exception(f"Not found function {handle_func} {handle_func}")

    _providers = {}
    # init state scanner
    state = RedisState(address=contract, event=event, handle_log=_func)
    for provider_uri in providers:
        _provider = Provider(provider_uri, request_kwargs={'timeout': 30})
        _provider.init_contract(contract_address=contract, abi_file=abi)

        _event_func = _provider.get_event_func(event)

        if not _event_func:
            raise Exception(f'Not found event {event}')

        _provider.init_scanner(state, _event_func)
        _providers[provider_uri] = _provider
    # default scanner
    provider_rpc = providers.pop()
    provider = _providers[provider_rpc]
    # provider.scanner.delete_potentially_forked_block_data(state.get_last_scanned_block())

    while True:
        try:

            LoggerTask.debug(f"[LOG] Start {'***' * 10} {contract} {event}")

            start_block = max(state.get_last_scanned_block(), INIT_BLOCK_NUMBER)
            end_block = provider.scanner.get_suggested_scan_end_block()

            def _update_progress(start, end, current, current_block_timestamp, chunk_size, events_count):
                if current_block_timestamp:
                    formatted_time = current_block_timestamp.strftime("%d-%m-%Y")
                else:
                    formatted_time = "no block time available"
                LoggerTask.debug(
                    f"[LOG]Current block: {current} ({formatted_time}), blocks in a scan batch: {chunk_size}, events processed in a batch {events_count}")

            LoggerTask.debug(f"[LOG] cron log start: {start_block} -> {end_block}")

            result, total_chunks_scanned = provider.scanner.scan(
                start_block,
                end_block,
                progress_callback=_update_progress)
        except:
            sentry_sdk.capture_exception()
            traceback.print_exc()
            old_rpc = f'{provider_rpc}'
            if not providers:
                LoggerTask.debug(f"[LOG] Cannot switch rpc => retry current rpc")
                sentry_sdk.capture_message("Cannot switch rpc => retry current rpc")
            else:
                provider_rpc = providers.pop()
                providers.append([old_rpc])
                provider = _providers[provider_rpc]
                LoggerTask.debug(f"[LOG] switch rpc: from {old_rpc} to {provider_rpc}")
                sentry_sdk.capture_message(f"switch rpc: from {old_rpc} to {provider_rpc}")

        if auto_remove_at and dt_utcnow().timestamp() > auto_remove_at:
            LoggerTask.debug(f"[LOG] end {'***' * 10} {contract} {event}")
            return

        LoggerTask.debug(f"[LOG] Sleep {'***' * 10} {contract} {event}")

        sleep(
            get(kwargs, 'interval', default=10)
        )


kw_dict = {}
for arg in sys.argv[1:]:
    if '=' in arg:
        sep = arg.find('=')
        key, value = arg[:sep], arg[sep + 1:]
        kw_dict[key] = value

if __name__ == "__main__":
    _bg_id = get(kw_dict, 'task_id')
    LoggerTask.debug(f"[LOG] Run task ____ {_bg_id}")

    background_job = BackgroundJobModel.db().find_one_and_update(filter={
        '_id': _bg_id if isinstance(_bg_id, ObjectId) else ObjectId(_bg_id)
    }, update={
        "$set": {
            "start_at": dt_utcnow(),
            "end_at": None
        }
    })

    try:
        run_logs(**background_job)
    except:
        sentry_sdk.capture_exception()
        traceback.print_exc()
    remove_task(_bg_id)

    BackgroundJobModel.db().find_one_and_update(filter={
        '_id': _bg_id if isinstance(_bg_id, ObjectId) else ObjectId(_bg_id)
    }, update={
        "$set": {
            "end_at": dt_utcnow()
        }
    })
