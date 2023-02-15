# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
import lib
from src.schemas.job import JobFormData
from src.services.background_job import JobService


@lib.handle_res(login=False, req_schema=JobFormData)
def add_job(body, *args, **kwargs):
    _form_data = body.__dict__
    _job = JobService.add(form_data=_form_data)

    return {
        'task_id': _job
    }


@lib.handle_res(login=False)
def restart(*args, **kwargs):
    _tasks = JobService.restart()
    return {
        'tasks': _tasks
    }
