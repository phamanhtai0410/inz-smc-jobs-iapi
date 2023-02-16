# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
import os
import subprocess

from pydash import get

from lib.logger import LoggerTask
from src.enums.job import JobType
from src.background import worker
from bson import json_util

_dict = os.getcwd()


@worker.task(name='worker.run_background_jobs', rate_limit='100/s')
def run_background_job(background_job):
    background_job = json_util.loads(background_job) if isinstance(background_job, str) else background_job
    _bg_id = get(background_job, '_id')
    _chain_name = get(background_job, 'chain')
    LoggerTask.debug(f"Start bg: {get(background_job, 'contract')} with event {get(background_job, 'event')}, on chain: {_chain_name}")

    LoggerTask.debug(f"_dict {_dict}")
    _program = f'TASK_ID_{_bg_id}'
    _command = None

    if JobType.GET_LOG == get(background_job, 'type'):
        LoggerTask.debug("Run GET_LOG")
        _command = f'python src/scripts/log.py task_id={_bg_id}'

    if JobType.LISTEN_EVENT == get(background_job, 'type'):
        LoggerTask.debug("Run LISTEN_EVENT")
        _command = f'python src/scripts/listener.py task_id={_bg_id} chain_name={_chain_name}'
    if not _command:
        raise Exception("Not found command")

    config_txt = f"""
    [program:{_program}]
    command={_command}
    directory=/webapps
    autostart=true
    autorestart=false
    redirect_stderr=true
    stdout_logfile=/dev/stdout
    stderr_logfile=/dev/stderr
    stdout_logfile_maxbytes=0
    stderr_logfile_maxbytes=0
    """
    _config_file_path = f"{_dict}/subprocess/{_bg_id}.conf"
    LoggerTask.debug(f"_config_file_path {_config_file_path}")

    with open(_config_file_path, 'w') as f:
        f.write(config_txt)

    subprocess.run(
        ["supervisorctl", "reread"], timeout=10)

    subprocess.run(
        ["supervisorctl", "update"], timeout=10)
    LoggerTask.debug(f"run subprocess {_config_file_path}")

    return "Job running"
    #

    #
    # if get(background_job, 'auto_remove_at'):
    #     return f"End event: {background_job}"
    # else:
    #     raise Exception(f"Stop background job: {background_job}")
