# Neolixir

Declarative ORM abstraction layer for Neo4j.

## Dependencies

The current stable version requires py2neo 1.4.6.

Future versions will support the latest 1.6.* versions of py2neo.

## Testing

Tests are based on pytest and are located in the tests/ directory.

Please make sure to run and update the tests if necessary after any development.

### Running tests

In order to run the tests:

1. Set up a neo4j instance running at localhost:7474 (**WARNING**: running the tests will clear the contents of this database)

2. Install virtualenv

3. The first time, you will need to build the test virtualenv:

    ```bash
    $ ./virtualenv/build.sh
    ```

4. From the repo root, activate the virtualenv and run the tests:

    ```bash
    $ source virtualenv/py2neo14/bin/activate
    $ py.test tests
    ```
