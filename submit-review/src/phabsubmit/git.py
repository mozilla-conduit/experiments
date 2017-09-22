# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from __future__ import absolute_import, unicode_literals

import logging
import pipes
import subprocess

logger = logging.getLogger(__name__)


class Git(object):
    """Helper class for running git commands"""

    def __init__(self, repo_path, secret=None):
        """
        :param repo_path: the full path to the git repo.
        :param logger: if set the command executed will be logged with
                       level info.
        :param secret: this string will be replaced with 'xxx' when logging.
        """
        self.repo_path = repo_path
        self.logger = logger
        self.secret = secret

    def cmd(self, *command):
        """ Run the specified command with git.

        eg. git.cmd('status', '--short')
        """
        assert command and len(command)
        command = ['git'] + list(command)
        if self.logger:
            command_str = ' '.join(map(pipes.quote, command))
            if self.secret:
                command_str = command_str.replace(self.secret, 'xxx')
            self.logger.info('$ %s' % command_str)
        subprocess.check_call(command, cwd=self.repo_path)

    def get(self, *command):
        """ Run the specified command with git and return the result.

        eg. diff = git.cmd('diff', '--no-color')
        """
        assert command and len(command)
        command = ['git'] + list(command)
        return subprocess.check_output(command, cwd=self.repo_path)

    def parse_revs(self, revs):
        """Return tuple(commits, parent, closest_remote).

        The returned tuple values will be the following:
        `commits` will be an iterable of commit nodes.
        `parent` is the parent of the earliest commit in `commits`.
        `closest_remote` is the commit closest to commits that is also remote.
        """
        # If revs was not provided default to everythong not on the remote.
        revs = self.rev_parse(*(revs or ('origin..HEAD',)))

        # Turn the revs into a proper list of commits
        n = len(revs)
        if not revs:
            commits = []
        elif n == 1:
            commits = revs
        else:
            commits = self.rev_list(*revs)

        if not commits:
            # Nothing to post for review
            return ([], None, None)

        return (
            commits,
            self.parent(commits[-1]),
            self.closest_ancestor_on_remote(commits[-1]),
        )

    def local_revs(self, rev, remote='origin'):
        return self.rev_list(rev, '--not', '--remotes={}'.format(remote))

    def rev_list(self, *args):
        stripped = self.get('rev-list', *args).strip()
        return stripped.split() if stripped else ()

    def rev_parse(self, *args):
        stripped = self.get('rev-parse', '--revs-only', *args)
        return stripped.split() if stripped else ()

    def parent(self, rev):
        return self.rev_parse('{}^'.format(rev))[0]

    def closest_ancestor_on_remote(self, rev, remote='origin'):
        local = self.local_revs(rev, remote=remote)
        return self.parent(local[-1]) if local else self.parent(rev)
