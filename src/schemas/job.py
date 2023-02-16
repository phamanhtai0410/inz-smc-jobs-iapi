# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""

from marshmallow import Schema, EXCLUDE, fields, validate

from lib.enums.chain import ChainCode
from src.enums.job import JobType


class JobFormData(Schema):
    class Meta:
        ordered = True
        unknown = EXCLUDE

    type = fields.Str(validate=validate.OneOf([
        JobType.GET_LOG,
        JobType.LISTEN_EVENT
    ]))
    contract = fields.Str(required=True)
    interval = fields.Int(missing=30,default=30)
    abi = fields.List(fields.Dict(), required=True)
    chain = fields.Str(
        validate=validate.OneOf([
            ChainCode.BSC,
            ChainCode.POLYGON,
            ChainCode.ETHER,
        ])
    )
    task = fields.Str()
    event = fields.Str()
    from_block = fields.Int(missing=0, default=0)
    auto_remove_at = fields.Float(missing=0, default=0)
    # kwargs = fields.Dict(missing={})
