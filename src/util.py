# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
import os
import subprocess
import traceback

import sentry_sdk

from lib.logger import Logger

_dict = os.getcwd()


def make_red_key(tx_hash, contract):
    return f'smc_cron_log:redlock\{contract}:{tx_hash}'


def remove_task(task_id):
    try:

        _id = task_id
        _program = f'TASK_ID_{_id}'

        _config_file_path = f"{_dict}/subprocess/{_id}.conf"
        Logger.debug(f"remove _config_file_path {_config_file_path}")

        if os.path.exists(_config_file_path):
            os.remove(_config_file_path)

            subprocess.run(
                ["supervisorctl", "reread"], timeout=10)
            subprocess.run(
                ["supervisorctl", "update"], timeout=10)

        Logger.debug(f"done remove {_config_file_path}")
    except:
        sentry_sdk.capture_exception()
        traceback.print_exc()
