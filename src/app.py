# -*- coding: utf-8 -*-

import sentry_sdk
from pymodm import connect
from sentry_sdk import capture_exception, capture_message
from sentry_sdk.integrations.flask import FlaskIntegration
from flask import Flask, request, jsonify

from lib.decorators.http import make_response
from lib.enums.database import DBName
from lib.enums.http import ErrorCode
from .config import DefaultConfig

# For import *
__all__ = ['create_app']


def create_app(config=None, app_name=None):
    """Create a Flask app."""
    if app_name is None:
        app_name = DefaultConfig.PROJECT

    app = Flask(app_name, instance_relative_config=True)
    configure_app(app, config)
    configure_hook(app)
    configure_extensions(app)
    configure_blueprints(app)
    configure_template_filters(app)
    configure_error_handlers(app)
    configure_logging_level()

    return app


def configure_app(app, config=None):
    """Different ways of configurations."""

    # http://flask.pocoo.org/docs/api/#configuration
    app.config.from_object(DefaultConfig)

    # http://flask.pocoo.org/docs/config/#instance-folders
    app.config.from_pyfile('production.cfg', silent=True)

    if config:
        app.config.from_object(config)


def configure_extensions(app):
    connect(DefaultConfig.DB_DAPP,alias=DBName.DAPP, connect=False)
    # mdb_payment.init_app(app, uri=app.config['MONGO_URI_INZ_PAYMENT'])

    # Sentry
    if DefaultConfig.SENTRY_DSN:
        sentry_sdk.init(
            dsn=DefaultConfig.SENTRY_DSN,
            integrations=[FlaskIntegration()],
            server_name=DefaultConfig.PROJECT
        )

        capture_message('{} starts'.format(DefaultConfig.PROJECT))


def configure_blueprints(app):
    """Configure blueprints in views."""
    from src.api import DEFAULT_BLUEPRINTS as blueprints
    for blueprint in blueprints:
        app.register_blueprint(
            blueprint,
            url_prefix=f'/{blueprint.url_prefix}'
        )


def configure_template_filters(app):
    @app.template_filter()
    def pretty_date(value):
        return pretty_date(value)

    @app.template_filter()
    def format_date(value, format='%Y-%m-%d'):
        return value.strftime(format)


def configure_logging_level():
    import logging
    logging.getLogger('suds').setLevel(logging.ERROR)


def configure_hook(app):
    @app.before_request
    def before_request():
        pass


def configure_error_handlers(app):
    @app.errorhandler(403)
    def forbidden_page(error):
        print(error)
        return make_response(msg="forbidden", error_code=ErrorCode.REQUIRED_AUTH), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return make_response(
            msg="Not Found: The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again",
            error_code=ErrorCode.BAD_REQUEST), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return make_response(msg="server error", error_code=ErrorCode.UNKNOWN_ERROR), 500
