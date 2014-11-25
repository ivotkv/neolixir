# Neolixir

Declarative ORM abstraction layer for Neo4j.

## Dependencies

The current stable version requires py2neo 2.0+, which requires Python 2.7+.

The legacy branch supports py2neo 1.4.6 with Python 2.6+.

## Testing

Tests are based on pytest and are located in the `tests/` directory.

Please make sure to run and update the tests if necessary after any development.

### Running tests

In order to run the tests:

1. Set up a neo4j instance running at `localhost:7474`. Alternatively, you may specify a different database using the `NEO4J_TEST_SERVER` variable, e.g. `NEO4J_TEST_SERVER=localhost:7480`.

    **WARNING**: running the tests will clear the contents of this database.

2. Make sure `pip` and `virtualenv` are installed.

3. The first time, you will need to build the test virtualenv:

    ```bash
    $ ./virtualenv/build.sh py2neo20
    ```

4. From the repo root, activate the virtualenv you wish to test against:

    ```bash
    $ source virtualenv/py2neo20/bin/activate
    ```

5. Run the tests:

    ```bash
    $ py.test tests
    ```
    Or, if your server is not at the default address:
    ```bash
    $ NEO4J_TEST_SERVER=localhost:7480 py.test tests
    ```
