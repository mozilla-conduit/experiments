# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from __future__ import absolute_import

import os

import betamax
import pytest
from betamax_serializers import pretty_json

from neotoma.app import create_app

PHABRICATOR_API_KEY = os.environ.get('TEST_PHABRICATOR_API_KEY', 'X' * 32)

with betamax.Betamax.configure() as config:
    config.cassette_library_dir = 'tests/cassettes/'
    betamax.Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
    config.default_cassette_options['serialize_with'] = 'prettyjson'
    config.default_cassette_options['record_mode'] = 'once'
    config.define_cassette_placeholder(
        '<PHAB_AUTH_TOKEN>', PHABRICATOR_API_KEY
    )


@pytest.fixture
def phabricator_api_key():
    return PHABRICATOR_API_KEY


@pytest.fixture
def app():
    """Needed for pytest-flask."""
    app = create_app(
        'https://phabricator-dev.allizom.org', '/repos', {
            'source': 'https://github.com/mozilla-conduit/neotoma',
            'version': None,
            'commit': None,
            'build': 'test',
        }
    )
    return app.app
