# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from flask import Blueprint

from .controller import health_check

rest_root = Blueprint('rest_root', __name__, url_prefix='')

rest_root.add_url_rule('/common/health_check', view_func=health_check)
