# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import contextlib
import logging
import os
import os.path

import hglib

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def wd(new=None):
    """Change the working directory temporarily."""
    old = os.getcwd()
    try:
        if new is not None:
            os.chdir(new)

        yield
    finally:
        os.chdir(old)


def ensure_updated_clone(path, remote):
    """Ensure path contains an up to date clone of the repo at remote."""
    # TODO: hg robustcheckout extension.
    if not os.path.exists(path):
        hglib.clone(source=remote, dest=path, noupdate=True)

    with hglib.open(path=path) as client:
        assert client.pull()


def get_hglib_client(path=None, bundle_path=None):
    """Return an hglib client with the provided bundle applied in memory.

    If path is not provided the cwd will be used. If bundle_path is not
    provided the client will be returned without the bundle applied.
    """
    path = path or os.getcwd()
    if bundle_path is not None:
        # Make sure the bundle path is absolute since
        # we're possibly changing the working directory.
        bundle_path = os.path.abspath(bundle_path)

    with wd(path):
        return hglib.open(path=bundle_path or path)


def generate_phabricator_diff(client, base, rev):
    """Return a diff properly formatted for Phabricator.

    The diff is generated between base and rev in the repository
    the hglib client `client` is connected to.
    """
    # Use git format and set the maximum lines of context.
    return client.diff(revs=[base, rev], git=True, unified=32767)
