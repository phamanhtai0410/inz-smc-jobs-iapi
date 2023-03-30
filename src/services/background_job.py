# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
import traceback

import sentry_sdk
from celery.worker.control import revoke
from pydash import get
from pymongo import ReturnDocument

from lib.logger import LoggerTask
from lib.utils import dt_utcnow
from src.models.background_job import BackgroundJobModel
from src.background_worker.script import run_background_job
from bson import json_util, ObjectId


class JobService(object):

    @classmethod
    def add(cls, form_data: dict):
        _job = BackgroundJobModel.db().find_one_and_update(filter={
            'contract': form_data['contract'].lower(),
            'event': form_data['event'],
            'chain': form_data['chain'],
            'type': form_data['type'],
            'task': form_data['task']
        }, update={
            '$set': {
                'interval': form_data['interval'],
                'abi': form_data['abi'],
                'from_block': form_data['from_block'],
                'auto_remove_at': 0
            }
        }, upsert=True, return_document=ReturnDocument.AFTER)
        if not _job.get('active'):
            return cls.start(_job)
        return _job['task_id']

    @classmethod
    def start(cls, job):
        _task = run_background_job.delay(
            json_util.dumps(job)
        )
        _job = BackgroundJobModel.update_one(
            filter={
                '_id': job['_id'] if not isinstance(job['_id'], ObjectId) else ObjectId(job['_id'])
            },
            obj={
                'task_id': str(_task),
                'active': True
            }
        )
        return str(_task)

    @classmethod
    def stop(cls, job_id):
        job = BackgroundJobModel.update_one(
            filter={
                '_id': job_id
            },
            obj={
                'active': False
            }
        )
        _task_id = get(job, 'task_id')
        if _task_id:
            try:
                revoke(task_id=_task_id, terminate=True)
            except:
                traceback.print_exc()
                sentry_sdk.capture_exception()
        return

    @classmethod
    def restart(cls):
        _jobs = BackgroundJobModel.db().find({
            "$or": [
                {"auto_remove_at": {
                    "$gt": dt_utcnow().timestamp()
                }},
                {"auto_remove_at": {
                    "$eq": 0
                }}
            ]
        })
        _tasks = []
        for _job in _jobs:
            _task = cls.start(_job)
            _tasks.append(_task)
        return _tasks
