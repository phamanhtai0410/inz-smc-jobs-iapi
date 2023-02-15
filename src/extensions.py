# -*- coding: utf-8 -*-
from flask_redis import Redis
from pymodm import connect

from rediscluster import RedisCluster
from redlock import Redlock
from web3 import Web3

from .config import DefaultConfig

# Redis cache
redis_cache = Redis()
# Redis user info, will initialized in app
redis_cluster = RedisCluster(
    startup_nodes=DefaultConfig.REDIS_CLUSTER,
    decode_responses=True,
    skip_full_coverage_check=True
)
# print('Init Redis user info successfully')
dlm = Redlock(DefaultConfig.REDLOCK_REDIS, retry_count=2)
bsc_web3 = Web3(Web3.HTTPProvider(DefaultConfig.BSC_RPC_URIS[0], request_kwargs={'timeout': 60})) 
