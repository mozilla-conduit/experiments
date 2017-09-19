# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from connexion.lifecycle import ConnexionResponse

from neotoma.decorators import require_phabricator_api_key


@require_phabricator_api_key
def noop(*args, **kwargs):
    return ConnexionResponse(status_code=200)


def test_require_phabricator_api_key_missing(app):
    with app.test_request_context('/', headers=[]):
        resp = noop()

    assert resp.status_code == 401


def test_require_phabricator_api_key_invalid(monkeypatch, app):
    monkeypatch.setattr(
        'neotoma.decorators.Phabricator.verify_auth',
        lambda *args, **kwargs: False
    )
    with app.test_request_context('/', headers=[('X-API-Key', 'x')]):
        resp = noop()

    assert resp.status_code == 403


def test_require_phabricator_api_key_valid(monkeypatch, app):
    monkeypatch.setattr(
        'neotoma.decorators.Phabricator.verify_auth',
        lambda *args, **kwargs: True
    )
    with app.test_request_context('/', headers=[('X-API-Key', 'x')]):
        resp = noop()

    assert resp.status_code == 200
