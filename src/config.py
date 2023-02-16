# -*- coding: utf-8 -*-

import os
import json
from dotenv import load_dotenv

load_dotenv()


class BaseConfig(object):
    PROJECT = "smc-jobs-iapi"

    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    DEBUG = False
    TESTING = False

    # http://flask.pocoo.org/docs/quickstart/#sessions
    SECRET_KEY = os.getenv("SECRET_KEY")


class DefaultConfig(BaseConfig):
    DEBUG = True

    # Flask-babel: http://pythonhosted.org/Flask-Babel/
    ACCEPT_LANGUAGES = ['vi']
    BABEL_DEFAULT_LOCALE = 'en'

    DB_DAPP = os.getenv('DB_DAPP')
    APP_PORT = os.getenv('APP_PORT', 5000)
    REDIS_CLUSTER = json.loads(os.getenv('REDIS_CLUSTER'))

    SENTRY_DSN = os.getenv('SENTRY_DSN')

    # Worker config
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
    CELERY_TASK_RESULT_EXPIRES = os.getenv('CELERY_TASK_RESULT_EXPIRES')
    CELERY_TASK_RESULT_EXPIRES = int(CELERY_TASK_RESULT_EXPIRES) if CELERY_TASK_RESULT_EXPIRES else 600
    CELERY_DEFAULT_QUEUE = 'background-job-queue'
    BG_CELERY_DEFAULT_QUEUE = 'background-queue'
    CELERY_ROUTES = {
        'worker.on_mint_nft': {'queue': CELERY_DEFAULT_QUEUE},
        'worker.run_background_jobs': {'queue': BG_CELERY_DEFAULT_QUEUE},
    }

    CELERY_TRACK_STARTED = True
    CELERY_ENABLE_UTC = True
    
    REDLOCK_REDIS = json.loads(os.getenv('REDLOCK_REDIS'))
    # print("REDLOCK_REDIS ", REDLOCK_REDIS)
    BSC_RPC_URIS = json.loads(os.getenv('BSC_RPC_URIS'))
    AVAX_RPC_URIS = json.loads(os.getenv('AVAX_RPC_URIS'))
    ETH_RPC_URIS = json.loads(os.getenv('ETH_RPC_URIS'))
    POLYGON_RPC_URIS = json.loads(os.getenv('POLYGON_RPC_URIS'))
    CELERY_IMPORTS = ['src.workers', 'src.background_worker']
    IAPI_NFT_URI = os.getenv('IAPI_NFT_URI')
