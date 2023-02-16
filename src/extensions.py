# -*- coding: utf-8 -*-
from flask_redis import FlaskRedis
from pymodm import connect

from rediscluster import RedisCluster
from redlock import Redlock
from web3 import Web3

from .config import DefaultConfig

# Redis cache
redis_cache = FlaskRedis()
# Redis user info, will initialized in app
redis_cluster = RedisCluster(
    startup_nodes=DefaultConfig.REDIS_CLUSTER,
    decode_responses=True,
    skip_full_coverage_check=True
)
# print('Init Redis user info successfully')
dlm = Redlock(DefaultConfig.REDLOCK_REDIS, retry_count=2)
bsc_web3 = Web3(Web3.HTTPProvider(DefaultConfig.BSC_RPC_URIS[0], request_kwargs={'timeout': 60})) 
ether_web3 = Web3(Web3.HTTPProvider(DefaultConfig.ETHEREUM_RPC_URIS[0], request_kwargs={'timeout': 60})) 
polygon_web3 = Web3(Web3.HTTPProvider(DefaultConfig.POLYGON_RPC_URIS[0], request_kwargs={'timeout': 60})) 
