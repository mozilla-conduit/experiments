# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import logging

import requests

logger = logging.getLogger(__name__)


class ConduitError(Exception):
    """Exception to be raised when Phabricator returns an error response."""

    def __init__(self, msg, error_code=None, error_info=None):
        super(ConduitError, self).__init__(msg)
        self.error_code = error_code
        self.error_info = error_info

    @classmethod
    def raise_if_error(cls, response_body):
        """Raise a ConduitError if the provided response_body was an error."""
        if response_body['error_code']:
            raise cls(
                response_body.get('error_info'),
                error_code=response_body.get('error_code'),
                error_info=response_body.get('error_info')
            )


class Phabricator(object):
    """Phabricator api client."""

    def __init__(self, url, api_key=None, session=None):
        self.url = url + 'api/' if url[-1] == '/' else url + '/api/'
        self.api_key = api_key
        self.session = session or self.create_session()

    @staticmethod
    def create_session():
        return requests.Session()

    @staticmethod
    def flatten_params(params):
        """Flatten nested objects and lists.

        Phabricator requires query data in a application/x-www-form-urlencoded
        format, so we need to flatten our params dictionary."""
        flat = {}
        remaining = list(params.items())

        # Run a depth-ish first search building the parameter name
        # as we traverse the tree.
        while remaining:
            key, o = remaining.pop()
            if isinstance(o, dict):
                gen = o.items()
            elif isinstance(o, list):
                gen = enumerate(o)
            else:
                flat[key] = o
                continue

            remaining.extend(('{}[{}]'.format(key, k), v) for k, v in gen)

        return flat

    def verify_auth(self):
        try:
            ConduitError.raise_if_error(
                self._request('GET', 'user.whoami').json()
            )
        except ConduitError:
            return False
        # If phabricator returned an error code authentication
        # failed, otherwise the api_key is valid.
        return True

    def get_repo(self, callsign):
        """Return the phabricator repo for a given callsign or None."""
        response = self._request(
            'GET',
            'diffusion.repository.search',
            phab_params={
                'constraints': {
                    'callsigns': [callsign]
                },
                'attachments': {
                    'uris': True,
                }
            }
        ).json()
        ConduitError.raise_if_error(response)
        items = response['result']['data']
        return items[0] if items else None

    def create_diff(self, diff, repo_phid=None):
        """Create a diff on phabricator and return the response."""
        params = {'diff': diff}
        if repo_phid is not None:
            params['repositoryPHID'] = repo_phid

        response = self._request(
            'GET', 'differential.createrawdiff', phab_params=params
        ).json()
        ConduitError.raise_if_error(response)
        return response['result']

    def create_revision(self, diff_phid, revision=None):
        """Create a revision on phabricator using an already created diff."""
        transactions = [
            {'type': 'update', 'value': diff_phid},
            {'type': 'title', 'value': 'TODO, title'},
            {'type': 'summary', 'value': 'TODO, summary'},
            {'type': 'testPlan', 'value': 'TODO, testPlan'},
            {
                'type': 'comment',
                'value': 'This revision was updated using Pack Rat. To '
                         'apply the exact commits used to create it locally '
                         'you can run the following command: '
                         '`hg import https://packrat.mozilla.com/bundle/todo`',
            }
        ]  # yapf: disable
        # TODO: Update the diff properties to include things like commit
        # information.
        # TODO: Flag reviewers
        # TODO: use a sensible title, summary, etc.

        params = {'transactions': transactions}
        if revision:
            params['objectIdentifier'] = revision

        response = self._request(
            'GET',
            'differential.revision.edit',
            phab_params=params,
        ).json()
        ConduitError.raise_if_error(response)
        return response['result']

    def _request(self, method, path, phab_params=None, **kwargs):
        url = self.url + path
        kwargs['data'] = kwargs.get('data', {})
        kwargs['data']['api.token'] = self.api_key

        if phab_params is not None:
            kwargs['data'].update(self.flatten_params(phab_params))

        return self.session.request(method, url, **kwargs)
