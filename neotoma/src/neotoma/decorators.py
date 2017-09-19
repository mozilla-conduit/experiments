# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import functools
import logging

from connexion import (
    problem,
    request,
)
from flask import current_app, g

from neotoma.phabricator import Phabricator

logger = logging.getLogger(__name__)


def require_phabricator_api_key(f):
    """Decorator which verifies phabricator API Key.

    Using this decorator on a connexion handler will require a phabricator
    api key be sent in the `X-API-Key` header of the request. If the header
    is not provided an HTTP 401 response will be sent.

    The provided API key will be verified to be valid, if it is not an
    HTTP 403 reponse will be sent.

    Decorated functions may assume X-API-Key header is present, contains
    a valid phabricator API key and flask.g.phabricator is a Phabricator
    client using this API Key.
    """

    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key is None:
            return problem(
                401,
                'X-API-Key Required',
                'Phabricator api key not provided in X-API-Key header',
                type='https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401' # noqa
            )  # yapf: disable

        phabricator = Phabricator(
            current_app.config['PHABRICATOR_URL'], api_key=api_key
        )
        if not phabricator.verify_auth():
            return problem(
                403,
                'X-API-Key Invalid',
                'Phabricator api key is not valid',
                type='https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/403' # noqa
            )  # yapf: disable

        g.phabricator = phabricator
        return f(*args, **kwargs)

    return wrapped
