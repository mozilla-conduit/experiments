# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from __future__ import absolute_import

import logging
import os.path

import connexion
from connexion.resolver import RestyResolver

from neotoma.dockerflow import dockerflow

logger = logging.getLogger(__name__)


def create_app(phabricator_url, repos_path, version_data):
    """Construct an application instance."""
    app = connexion.App(__name__, specification_dir='specifications/')
    app.add_api('neotoma.yml', resolver=RestyResolver('neotoma.api'))

    # Get the Flask app being wrapped by the Connexion app.
    flask_app = app.app
    flask_app.config['PHABRICATOR_URL'] = phabricator_url
    flask_app.config['REPOS_PATH'] = os.path.abspath(repos_path)
    flask_app.config['VERSION_DATA'] = version_data

    flask_app.register_blueprint(dockerflow)

    return app
