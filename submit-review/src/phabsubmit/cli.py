import json

import click
from dulwich.errors import NotGitRepository
from dulwich.repo import Repo

from phabsubmit.git import Git
from phabsubmit.phabricator import Phabricator


UPDATED_REVISION = """
Phabricator revision D{revision_id} successfully updated.

{revision_url}
""".strip()

CREATED_REVISION = """
Successfully created Phabricator revision D{revision_id}.

{revision_url}
""".strip()


@click.group()
def mozphab():
    """Mozilla client tools for Phabricator."""
    pass


@mozphab.command()
@click.pass_context
@click.option(
    '--phabricator-url', envvar='PHABRICATOR_URL',
    default='https://phabricator-dev.allizom.org/'
)
@click.option(
    '--phabricator-api-key', envvar='PHABRICATOR_API_KEY', default=None
)
@click.option('--repo-callsign', default='NSS')
@click.option(
    '-u', '--update-revision', default=None,
    help='Update the specified phabricator revision number')
@click.argument('revs', nargs=-1)
def submit(
    ctx,
    phabricator_url,
    phabricator_api_key,
    repo_callsign,
    update_revision,
    revs,
):
    """Submit a change to phabricator for review."""
    phabricator = Phabricator(phabricator_url, api_key=phabricator_api_key)
    if not phabricator.verify_auth():
        print 'Authentication failed, please provide a valid api key.'
        ctx.exit(1)

    try:
        repo = Repo.discover()
    except NotGitRepository:
        print 'A git repository could not be found.'
        ctx.exit(1)

    repo_path = repo.controldir()
    git = Git(repo.controldir())
    commits, parent, remote_base = git.parse_revs(revs)

    if not commits:
        print 'Nothing to review'
        ctx.exit(1)

    # Generate the diff for phabricator.
    diff = git.get('diff', '-U32767', '{}..{}'.format(parent, commits[0]))
    if not diff:
        print 'No difference, nothing to review'
        ctx.exit(1)

    repo = phabricator.get_repo(repo_callsign)
    if repo is None:
        print '{} repository cannot be found'.format(repo_callsign)
        ctx.exit(1)

    # Create/Update the phabricator revision.
    diff_result = phabricator.create_diff(diff, repo_phid=repo['phid'])
    phabricator.set_diff_properties(diff_result, remote_base, parent)
    revision_result = phabricator.create_revision(
        diff_result, revision=update_revision
    )

    msg = UPDATED_REVISION if update_revision else CREATED_REVISION
    print msg.format(
        revision_id=revision_result['object']['id'],
        revision_url=phabricator_url + 'D{}'.format(
            revision_result['object']['id']))
