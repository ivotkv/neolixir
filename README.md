# Neolixir

A declarative ORM abstraction layer for Neo4j. Provides model definition via polymorphic classes, schema definition, property typing, query abstraction, event handling and session management.

## Documentation

Detailed documentation coming soon. In the meantime, please see the Quick Start section below.

## Quick Start

### Installation

The current stable version requires py2neo 2.0, which requires Python 2.7+.

**NOTE**: Neo4j 3.0+ and Python 3.0+ support is currently still under development.

Since the package is not yet on PyPI, please install from GitHub directly:
```bash
pip install "git+https://git@github.com/ivotkv/neolixir.git"
```

### Basic Usage

Define a model:
```python
from neolixir import *

class Person(Node):
    name = String()
    born = DateTime()
    friends = RelOut('friends_with')
```

Set some values:
```
>>> bob = Person()
>>> bob
<Person (0x16cf310): 
Id = None
Descriptors = ['born', 'friends', 'name']
Properties = {}
>
>>> bob.name = 'Bob'
>>> bob.born = '1970-01-01'
>>> bob
<Person (0x16cf310): 
Id = None
Descriptors = ['born', 'friends', 'name']
Properties = {'born': '1970-01-01 00:00:00', 'name': u'Bob'}
>
```

Add a friend:
```
>>> alice = Person()
>>> alice.name = 'Alice'
>>> bob.friends.append(alice)
<Relationship (0x16ef850): (None)-[None:friends_with]->(None) {}>
>>> bob.friends
[<Person (0x16e83d0): 
Id = None
Descriptors = ['born', 'friends', 'name']
Properties = {'name': u'Alice'}
>]
```

If your Neo4j server requires authentication:
```
>>> metadata.authenticate('user', 'password')
True
```

Commit the session:
```
>>> metadata.session.commit()
>>> bob.id
315
>>> alice.id
316
```

Reload from database:
```
>>> metadata.session.clear()
>>> bob = Person.get(315)
>>> bob
<Person (0x17971d0): 
Id = 315
Descriptors = ['born', 'friends', 'name']
Properties = {u'born': u'1970-01-01 00:00:00', u'name': u'Bob', u'__class__': u'Person'}
>
>>> bob.friends
[<Person (0x17c3210): 
Id = 316
Descriptors = ['born', 'friends', 'name']
Properties = {u'name': u'Alice', u'__class__': u'Person'}
>]
>>> bob.friends.rels()
[<Relationship (0x17c3050): (315)-[155:friends_with]->(316) {u'__class__': u'Relationship'}>]
```

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

Developed and maintained by [Ivo Tzvetkov](https://github.com/ivotkv) at [ChallengeU](http://challengeu.com). Twitter: [@ivotkv](https://twitter.com/ivotkv). Gmail: ivotkv.

Copyright (c) 2013 Ivaylo Tzvetkov, ChallengeU. Released under the terms of the [MIT License](https://opensource.org/licenses/MIT).
