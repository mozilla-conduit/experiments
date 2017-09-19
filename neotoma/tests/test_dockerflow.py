# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


def test_lbheartbeat_returns_200(client):
    assert client.get('/__lbheartbeat__').status_code == 200


def test_version_response(client):
    response = client.get('/__version__')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert all(
        key in response.json
        for key in ('source', 'version', 'commit', 'build')
    )


def test_heartbeat_returns_200(client):
    assert client.get('/__heartbeat__').status_code == 200
