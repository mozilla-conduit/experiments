#!/usr/bin/env python
import hashlib
import os
import tempfile

import click
import hglib
import requests


@click.command()
@click.option(
    '--packrat-url', envvar='PACKRAT_URL', default='http://localhost:8888'
)
@click.option(
    '--phabricator-api-key', envvar='PHABRICATOR_API_KEY', default=None
)
@click.option('--repo-callsign', default='NSS')
@click.option('-u', '--update-revision', default=None)
@click.argument('rev', default='. or (draft() and ancestors(.))')
def main(
    packrat_url,
    phabricator_api_key,
    repo_callsign,
    update_revision,
    rev
):
    """Pack Rat test client."""
    submit_url = packrat_url + '/request-review'
    s = requests.session()
    s.headers['X-API-Key'] = phabricator_api_key

    hg = hglib.open()
    log = hg.log(revrange=rev)
    first = log[0].node
    last = log[-1].node
    data = {
        'repository_callsign': repo_callsign,
        'first': first,
        'last': last,
    }
    print 'first: {}'.format(first)
    print 'last: {}'.format(last)
    if update_revision:
        data['revision_id'] = update_revision

    bundle = tempfile.NamedTemporaryFile(
        suffix='.bundle', prefix='tmp-', delete=False)
    bundle.close()
    print bundle.name
    try:
        assert hg.bundle(bundle.name, rev='last({})'.format(rev))
        with open(bundle.name, 'rb') as b:
            req = requests.Request('POST', submit_url, data=data, files=[
                ('bundle', ('uploaded.bundle', b, 'application/octet-stream')),
            ])
            prep = s.prepare_request(req)
            resp = s.send(prep)
    finally:
        os.unlink(bundle.name)

    j = resp.json()
    if 'diff' in j:
        print j['diff']['uri']
    if 'revision_result' in j:
        print 'Revision D{}'.format(j['revision_result']['object']['id'])


if __name__ == '__main__':
    main()
