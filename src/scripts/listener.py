# -*- coding: utf-8 -*-

"""
   Description:
        -
        -
"""

import json
import sys
import traceback
import asyncio
from datetime import datetime, timezone

import sentry_sdk
from bson import ObjectId
from pydash import get
from pymodm import connect

sys.path.append(".")

from src.scripts.logger import LoggerTask

from src.models.background_job import BackgroundJobModel

from src.extensions import dlm
from src.util import make_red_key, remove_task
import src.workers as workers
import pydash
from web3 import Web3


class DBName:
    DAPP = 'inz-dapp'


def dt_utcnow():
    return datetime.utcnow().replace(tzinfo=timezone.utc)


from src.config import DefaultConfig

connect(DefaultConfig.DB_DAPP, alias=DBName.DAPP, connect=False)


class Provider(object):

    def __init__(self, provider, *args, **kwargs):
        self.contract = None
        self.web3 = Web3(Web3.HTTPProvider(provider, *args, **kwargs))

    def set_contract(self, contract, abi):
        self.contract = self.web3.eth.contract(address=contract, abi=abi)


#
# kw_dict = {}
# for arg in sys.argv[1:]:
#     if '=' in arg:
#         sep = arg.find('=')
#         key, value = arg[:sep], arg[sep + 1:]
#         kw_dict[key] = value


def handle_event(event, wk_handle, provider):
    try:
        _event = Web3.toJSON(event)
        _json = json.loads(_event)
        _json['transactionHash'] = _json['transactionHash'].lower()

        _tx_hash = pydash.get(_json, 'transactionHash')

        LoggerTask.debug(f'[EVENT] event')
        if _tx_hash:

            _key = make_red_key(
                tx_hash=_tx_hash,
                contract=pydash.get(_json, 'address').lower()
            )

            _lock = dlm.lock(_key, 60 * 5)
            LoggerTask.debug(f'[EVENT] 🔑 🔑 🔑 Key lock: {_key}')

            if _lock:
                LoggerTask.debug(f'[EVENT] \033[92m ✔✔✔ Process .................. {provider} \033[0m')
                wk_handle.delay(_json)
            else:
                LoggerTask.debug(f'[EVENT] \033[93m ⚠⚠⚠ ______ Lock fail ______ {provider} \033[0m')

    except:
        sentry_sdk.capture_exception()
        traceback.print_exc()


class EventListener():

    def __init__(self, provider, *args, **kwargs):
        # threading.Thread.__init__(self)
        self.contract_address = None
        self.callback = None
        self.event = None
        self.contract = None
        self.provider = provider
        self.web3 = Web3(Web3.HTTPProvider(provider, *args, **kwargs)) 

    def set_handle(self, event, callback):
        self.event = event
        self.callback = callback

    def init_contract(self, contract_address, abi_file):
        self.contract_address = contract_address
        self.contract = self.web3.eth.contract(address=Web3.toChecksumAddress(contract_address), abi=abi_file)

    def run(self, auto_remove_at=0) -> None:
        # asynchronous defined function to loop
        # this loop sets up an event filter and is looking for new entires for the "PairCreated" event
        # this loop runs on a poll interval

        async def log_loop(event_filter, poll_interval, callback, provider):
            while True:
                for evt in event_filter.get_new_entries():
                    try:
                        handle_event(evt, callback, provider)
                    except Exception as e:
                        print(e)
                        print('Error', provider)
                        traceback.print_exc()
                await asyncio.sleep(poll_interval)

        _run = True
        while _run:
            try:
                LoggerTask.debug(f'[EVENT] Start {"**" * 5} {self.contract_address} {self.event}')

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                _lastBlock = 'latest'
                try:
                    _event_func = getattr(self.contract.events, self.event)
                    event_filter = _event_func.createFilter(
                        fromBlock='latest'
                    )
                    LoggerTask.debug(f"[EVENT]  Start listening to event {_event_func} ... {event_filter}")
                    loop.run_until_complete(
                        asyncio.gather(
                            log_loop(event_filter, 2, self.callback, self.provider)
                        ))
                except Exception as e:
                    traceback.print_exc()
                finally:
                    loop.close()
                if auto_remove_at and dt_utcnow().timestamp() > auto_remove_at:
                    _run = False
            except:
                traceback.print_exc()


def run_listener(**kwargs):
    contract = kwargs['contract']

    providers = getattr(DefaultConfig, f'{kwargs["chain"]}_RPC_URIS')
    event = kwargs['event']
    abi = kwargs['abi']
    handle_func = kwargs['task']
    LoggerTask.debug(f'[EVENT]  {"**" * 5} Start Event')
    LoggerTask.debug(f'[EVENT]  {"**" * 5}  {contract}  {event}')

    _func = getattr(workers, handle_func)
    if isinstance(abi, str):
        with open(abi) as file:
            abi = json.load(file)

    if not _func:
        raise Exception(f"Not found function {handle_func} {handle_func}")

    _providers = []
    for provider_uri in providers:
        _provider = EventListener(provider_uri, request_kwargs={'timeout': 30})
        _provider.init_contract(contract_address=contract, abi_file=abi)
        _provider.set_handle(event=event, callback=_func)
        _providers.append(_provider)
    _providers[0].run(auto_remove_at=get(kwargs, 'auto_remove_at', 0))


kw_dict = {}
for arg in sys.argv[1:]:
    if '=' in arg:
        sep = arg.find('=')
        key, value = arg[:sep], arg[sep + 1:]
        kw_dict[key] = value

if __name__ == "__main__":
    _bg_id = get(kw_dict, 'task_id')
    LoggerTask.debug(f"[EVENT] Run task ____ {_bg_id} ____ ")
    background_job = BackgroundJobModel.db().find_one_and_update(filter={
        '_id': _bg_id if isinstance(_bg_id, ObjectId) else ObjectId(_bg_id)
    }, update={
        "$set": {
            "start_at": dt_utcnow(),
            "end_at": None
        }
    })
    try:
        run_listener(**background_job)
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
