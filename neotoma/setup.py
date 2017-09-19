# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='neotoma',
    version='0.1',
    description='Mozilla\'s Pack Rat, storing commits away in its "midden"',
    long_description=long_description,
    url='https://github.com/mozilla-conduit/neotoma',
    author='Mozilla',
    author_email='dev-version-control@lists.mozilla.org',
    license='MPL 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='mozilla commits development conduit',
    packages=find_packages('src'),
    package_data={'neotoma': ['spec/swagger.yml']},
    package_dir={'neotoma': 'src'},
    install_requires=[],
    extras_require={},
    entry_points={'console_scripts': ['neotoma = neotoma.cli:neotoma']},
)
