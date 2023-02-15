# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
import lib


@lib.handle_res(login=False)
def debug():
    return {}


@lib.handle_res(login=False)
def health_check(*args, **kwargs):
    return {}
