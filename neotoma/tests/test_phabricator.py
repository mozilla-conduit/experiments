# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from neotoma.phabricator import ConduitError, Phabricator


@pytest.fixture
def phabricator(phabricator_api_key, betamax_session):
    # requests advertises gzip support by default (as it should!). However,
    # This means that HTTP response bodies are base64 encoded in the cassette
    # JSON, making them difficult to diff and audit for sensitive data. Since
    # the encoding of the HTTP response body isn't important for our testing,
    # disable it.
    betamax_session.headers.update({'Accept-Encoding': 'identity'})
    return Phabricator(
        'https://phabricator-dev.allizom.org/',
        api_key=phabricator_api_key,
        session=betamax_session
    )


def test_phabricator_auth_invalid_api_key(phabricator):
    # Replace the real API key with a fake.
    phabricator.api_key = 'api-invalid' + ('x' * 21)
    assert not phabricator.verify_auth()


def test_phabricator_auth_valid_api_key(phabricator):
    assert phabricator.verify_auth()


def test_phabricator_get_repo_phid_none(phabricator):
    assert phabricator.get_repo('NOTAREALCALLSIGN') is None


def test_phabricator_get_repo_phid(phabricator):
    assert phabricator.get_repo(
        'MOZILLACENTRAL'
    )['phid'] == ('PHID-REPO-myz5mwsn6hrgkxn2ndos')  # yapf: disable


def test_conduiterror_raise_if_error(phabricator):
    # A passing call shouldn't raise.
    body = phabricator._request('GET', 'user.whoami').json()
    ConduitError.raise_if_error(body)

    # Calling with invalid parameters should result in an error.
    body = phabricator._request(
        'GET',
        'diffusion.repository.search',
        phab_params={
            'constraints': {
                'notavalidcontraint': ['x'],
            },
        }
    ).json()

    # Make sure this is an error response.
    assert body['error_code']
    with pytest.raises(ConduitError):
        ConduitError.raise_if_error(body)


def test_flatten_params(phabricator):
    flat = phabricator.flatten_params({
        'number': 10,
        'string': 'Hello There',
        'dictionary': {
            'number': 11,
            'nested-dictionary': {
                'number': 12,
                'string': 'Hello There Again',
            },
            'nested-list': [
                'a',
                'b',
                1,
                2,
            ]
        },
        'list': [
            13,
            'Hello You',
            {
                'number': 14,
                'string': 'Goodbye'
            },
            [
                'listception',
            ]
        ]
    })  # yapf: disable
    assert (
        flat == {
            'number': 10,
            'string': 'Hello There',
            'dictionary[number]': 11,
            'dictionary[nested-dictionary][number]': 12,
            'dictionary[nested-dictionary][string]': 'Hello There Again',
            'dictionary[nested-list][0]': 'a',
            'dictionary[nested-list][1]': 'b',
            'dictionary[nested-list][2]': 1,
            'dictionary[nested-list][3]': 2,
            'list[0]': 13,
            'list[1]': 'Hello You',
            'list[2][number]': 14,
            'list[2][string]': 'Goodbye',
            'list[3][0]': 'listception',
        }
    )
