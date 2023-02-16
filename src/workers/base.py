# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
import sentry_sdk
from celery import Task
import celery

from lib.logger import Logger


class ScriptBase(celery.Task):
    'A minimal custom request to log failures and hard time limits.'

    def on_timeout(self, soft, timeout):
        super(ScriptBase, self).on_timeout(soft, timeout)
        if not soft:
            sentry_sdk.capture_message(f"Timeout task {soft}")
            Logger.debug("Timeout task")

        self.retry()

    def on_failure(self, exc_info, send_failed_event=True, return_ok=False):
        super().on_failure(
            exc_info,
            send_failed_event=send_failed_event,
            return_ok=return_ok
        )
        Logger.warning(
            'Failure detected for task %s',
            self.task.name
        )


class MyTask(Task):
    Request = MyReques
