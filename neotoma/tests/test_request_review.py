# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


def test_no_bundle_returns_400(client):
    response = client.post(
        '/request-review',
        data={
            'repository_callsign': 'MOZILLACENTRAL',
            'first': '1' * 40,
            'last': '1' * 40,
        }
    )
    assert response.status_code == 400
    assert response.json['detail'] == 'Missing formdata parameter \'bundle\''
