# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import py
import pytest
import hglib

from neotoma import hg


@pytest.fixture
def hg_repo(tmpdir):
    """Return the path to a temporary directory with a testing hg repo."""
    hglib.clone(
        source='tests/data/repos/hg-simple',
        dest=tmpdir.strpath,
        noupdate=True
    )
    return tmpdir


def test_hglib_client_bundle_in_memory(hg_repo):
    applied = hg.get_hglib_client(
        path=hg_repo.strpath, bundle_path='tests/data/hg-simple-01.bundle'
    )
    assert applied.log()[0].node == '22213970cd4277baf32a4ca2d7eb7571065bb024'

    # Now check without the bundle that the commit
    # is missing.
    clean = hg.get_hglib_client(path=hg_repo.strpath)
    assert clean.log()[0].node != '22213970cd4277baf32a4ca2d7eb7571065bb024'


def test_generate_phabricator_diff(hg_repo):
    client = hg.get_hglib_client(
        path=hg_repo.strpath, bundle_path='tests/data/hg-simple-01.bundle'
    )
    diff = hg.generate_phabricator_diff(client, 0, 1)
    assert diff == (
        b'diff --git a/README b/README\n'
        b'--- a/README\n'
        b'+++ b/README\n'
        b'@@ -1,1 +1,1 @@\n'
        b'-Minimal hg repo for testing\n'
        b'+Changed README\n'
    )


def test_ensure_updated_clone(tmpdir):
    test_data = py.path.local('tests/data/repos/hg-simple')
    upstream_path = tmpdir.join('upstream')
    test_data.copy(upstream_path)

    clone_path = tmpdir.join('clone')
    # The path shouldn't exist yet.
    assert not clone_path.check()

    hg.ensure_updated_clone(clone_path.strpath, upstream_path.strpath)
    with hg.get_hglib_client(path=clone_path.strpath) as c:
        assert c.log()[0].node == 'ed0926b360d636818a70e54717b2e321845771cd'

    with hglib.open(path=upstream_path.strpath) as c:
        assert c.update()
        upstream_path.join('README').remove()
        c.commit(
            message='Delete the README',
            addremove=True,
            user='Test User <test@example.com>',
            date='1 0',
        )

    hg.ensure_updated_clone(clone_path.strpath, upstream_path.strpath)
    with hg.get_hglib_client(path=clone_path.strpath) as c:
        # The old commit should no longer be the latest
        assert c.log()[0].node != 'ed0926b360d636818a70e54717b2e321845771cd'
