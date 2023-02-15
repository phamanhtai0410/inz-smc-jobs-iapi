# -*- coding: utf-8 -*-

from gevent import monkey
monkey.patch_all()

from src import create_app
from flask_script import Manager

app = create_app()
manager = Manager(app)


@manager.command
def run():
    """Run in local machine."""
    app.run(host='0.0.0.0', debug=False)


manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")

if __name__ == "__main__":
    manager.run()
