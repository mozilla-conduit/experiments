# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from __future__ import absolute_import

import hashlib
import logging
import os.path
import tempfile

from connexion import problem
from flask import current_app, g, jsonify

from neotoma import hg
from neotoma.decorators import require_phabricator_api_key

logger = logging.getLogger(__name__)


@require_phabricator_api_key
def post(repository_callsign, first, last, bundle, revision_id=None):
    """Request review on commits uploaded in a mercurial bundle"""
    repo = g.phabricator.get_repo(repository_callsign)
    if repo is None:
        return problem(
            404,
            'Phabricator Repository not found',
            '{} repository cannot be found'.format(repository_callsign),
            type='https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404'
        )

    # Find the url which phabricator is observing from, that's where
    # we want to clone/update from.
    for uri in repo['attachments']['uris']['uris']:
        if uri['fields']['io']['effective'] == 'observe':
            break
    else:
        return problem(
            404,
            'Cannot find repository url',
            'A url for cloning/updating cannot be found for '
            '{}'.format(repository_callsign),
            type='https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404'
        )

    clone_url = uri['fields']['uri']['effective']

    # Calculate the path to the repository on the local filesystem.
    local_repo_name = hashlib.sha1(clone_url).hexdigest()
    repo_path = os.path.join(current_app.config['REPOS_PATH'], local_repo_name)
    hg.ensure_updated_clone(repo_path, clone_url)

    # Save the bundle to a temporary file.
    tmp_bundle = tempfile.NamedTemporaryFile(
        suffix='.bundle', prefix='tmp-uploaded-', delete=False
    )
    try:
        bundle.save(tmp_bundle)
        tmp_bundle.close()

        client = hg.get_hglib_client(
            path=repo_path, bundle_path=tmp_bundle.name
        )
        diff = hg.generate_phabricator_diff(
            client, 'p1({})'.format(first), last
        )
    finally:
        try:
            tmp_bundle.close()
        except:
            pass
        try:
            os.unlink(tmp_bundle.name)
        except:
            pass

    diff_result = g.phabricator.create_diff(diff, repo_phid=repo['phid'])
    revision_result = g.phabricator.create_revision(
        diff_result['phid'], revision=revision_id
    )

    return jsonify(
        {
            'diff': diff_result,
            'revision_result': revision_result,
            'bundle': tmp_bundle.name,
        }
    )
