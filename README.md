# Neolixir

A declarative ORM abstraction layer for Neo4j. Provides model definition via polymorphic classes, schema definition, property typing, query abstraction, event handling and session management.

## Documentation

## Quick Start

### Installation

The current stable version requires py2neo 2.0+, which requires Python 2.7+.

Since the package is not yet on PyPI, please install from GitHub directly:
```bash
pip install "git+ssh://git@github.com/Didacti/neolixir.git"
```

### Basic Usage

## Development

This software is open-source and released under the [MIT License](https://en.wikipedia.org/wiki/MIT_License). Feel free to clone, modify and contribute.

If contributing code, please follow the existing coding style and make sure to run and update the tests.

### Running the Tests

Tests are based on [pytest](http://pytest.org/) and are located in the `tests/` directory.

In order to run the tests:

1. Set up a neo4j instance running at `localhost:7474`. Alternatively, you may specify a different database using the `NEO4J_TEST_SERVER` variable, e.g. `NEO4J_TEST_SERVER=localhost:7480`.

    **WARNING**: running the tests will clear the contents of this database.

2. Make sure the `virtualenv` Python package is installed.

3. Clone this repo and go to its root directory.

4. The first time, you will need to build the test virtualenv:

    ```bash
    $ ./virtualenv/build.sh
    ```

5. Activate the virtualenv you wish to test against, by default:

    ```bash
    $ source ./virtualenv/python-2.7-py2neo-2.0.8/bin/activate
    ```

6. Run the tests:

    ```bash
    $ py.test tests
    ```
    Or, if your server is not at the default address:
    ```bash
    $ NEO4J_TEST_SERVER=localhost:7480 py.test tests
    ```

## About

Developed and maintained by [Ivo Tzvetkov](https://github.com/ivotkv) at [ChallengeU](http://challengeu.com). Inspired by the [Elixir](http://elixir.ematia.de/apidocs/elixir.html) wrapper for [SQLAlchemy](http://www.sqlalchemy.org/).

Copyright (c) 2013 Ivaylo Tzvetkov, ChallengeU. Released under the terms of The MIT License.
