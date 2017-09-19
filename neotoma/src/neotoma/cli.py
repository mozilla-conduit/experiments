# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from __future__ import absolute_import

import logging
import os

import click

from neotoma.app import create_app

logger = logging.getLogger(__name__)


@click.group()
def neotoma():
    """Mozilla's Pack Rat"""
    pass


@neotoma.command(name='dev-server')
@click.option('--debug', envvar='DEBUG', is_flag=True)
@click.option('--port', envvar='PORT', default=8888)
@click.option(
    '--phabricator-url', envvar='PHABRICATOR_URL', default='http://localhost'
)
@click.option('--repos-path', envvar='REPOS_PATH', default='/repos')
def dev_server(debug, port, phabricator_url, repos_path):
    """Run the development server.

    This server should not be used for production deployments. Instead
    the application should be served by an external webserver as a wsgi
    app.
    """
    app = create_app(
        phabricator_url, repos_path, {
            'source': 'https://github.com/mozilla-conduit/neotoma',
            'version': None,
            'commit': None,
            'build': 'dev',
        }
    )
    app.run(debug=debug, port=port)


@neotoma.command(context_settings=dict(ignore_unknown_options=True))
@click.argument('pytest_arguments', nargs=-1, type=click.UNPROCESSED)
def pytest(pytest_arguments):
    """Run pytest"""
    os.execvp('pytest', ('pytest', ) + pytest_arguments)


@neotoma.command(name='format-code')
@click.option('--in-place', '-i', is_flag=True)
def format_code(in_place):
    """Format python code"""
    os.execvp(
        'yapf',
        ('yapf', '--recursive', '--in-place' if in_place else '--diff', '.', )
    )
