# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from flask import Blueprint

from .controller import add_job, restart

rest_jobs = Blueprint('rest_jobs', __name__, url_prefix='background')
rest_jobs.add_url_rule('add', methods=['POST'], view_func=add_job)
rest_jobs.add_url_rule('restart', methods=['POST'], view_func=restart)

