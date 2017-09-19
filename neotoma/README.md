# Pack Rat (Neotoma)

A microservice that accepts mercurial bundles for submission to Phabricator.
These bundles are stored away permanently to provide commit-identical
reproduction of code posted for review.

Part of Mozilla
[Conduit](https://wiki.mozilla.org/EngineeringProductivity/Projects/Conduit),
our code management microservice ecosystem.

## Development

The neotoma development environment makes use of docker-compose. Developers
may find the following commands useful:

* Start development environment: `docker-compose up`
* Run the tests: `docker-compose run neotoma pytest`
* Auto format the code: `docker-compose run neotoma format-code -i`
* Print command help information: `docker-compose run neotoma --help`
* Run other neotoma commands: `docker-compose run neotoma <command>`

## Recording New Test Cassettes

Recording new cassettes for the tests requires hitting live systems on
the internet and a bit of configuration. Create a
`docker-compose.override.yml` file with the following contents (replacing
`<placeholder>` with the required values):
```
version: '2'
services:
  neotoma:
    environment:
      # A Valid api key for your account on phabricator-dev.
      - TEST_PHABRICATOR_API_KEY=<placeholder>
```
