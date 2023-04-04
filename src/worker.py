# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from pymodm import connect

from lib.enums.database import DBName
from lib.worker import create_worker
from src.config import DefaultConfig
import time

connect(DefaultConfig.DB_DAPP, alias=DBName.DAPP,connect=False)
worker = create_worker(DefaultConfig)

from celery.signals import worker_ready
import requests
from models import BackgroundJobsModel


@worker_ready.connect()
def message_poll_start(sender=None, headers=None, body=None, **kwargs):
    # sleep for sure api start
    time.sleep(60)
    print('-'*10, 'WORKER START', '-'*10)
    requests.post(f'{DefaultConfig.SMC_JOBS_IAPI_URI}/background/restart')
    print('-'*10, 'DONE RESTART WORKER', '-'*10)
