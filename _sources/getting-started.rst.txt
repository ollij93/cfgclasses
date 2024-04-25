Getting Started
===============
This page will guide you through getting started with a simple python
application using cfgclasses to define the command line interface.
For more details on the features of cfgclasses, see the :doc:`API <api>` documentation.

Installation
------------
Install using pip:

.. code-block:: bash

    $ pip install cfgclasses


We recommend using the latest available version of python, cfgclasses supports
python 3.10 and above.

A simple application
--------------------
A simple python application using cfgclasses looks like this:

.. code-block:: python

    import dataclasses
    import sys
    from cfgclasses import arg, parse_args

    @dataclasses.dataclass
    class MyConfig:
        """A simple example application"""
        name: str = arg("Your name")
        num: int = arg("An integer option", default=0)

    if __name__ == "__main__":
        config = parse_args(MyConfig, sys.argv[1:])
        print(f"Hello, {config.name}! Your number was: {config.num}")

And an example run of this application:

.. code-block:: bash

    $ python example.py --help
    usage: example.py [-h] [--name NAME] [--num NUM]

    options:
      -h, --help   show this help message and exit

      --name NAME  Your name
      --num NUM    An integer option

    $ python example.py --name Olli --num 42
    Hello, Olli! Your number was: 42

Common patterns
---------------
cfgclasses comes with utilty methods to reduce the volume of code required to define an applications interface. The most common of these has already been seen in the example above: ``arg(helpstr)``.

.. autofunction:: cfgclasses::arg
    :no-index:

The other common pattern is to use ``optional(helpstr)`` which is the same as ``arg(helpstr, default=None)``. This is useful for defining optional arguments that can be passed to the application.

.. code-block:: python

    import dataclasses
    import sys
    from cfgclasses import arg, optional, parse_args

    @dataclasses.dataclass
    class MyConfig:
        """A simple example application"""
        name: str = arg("Your name")
        num: Optional[int] = optional("An optional integer option")

    if __name__ == "__main__":
        config = parse_args(MyConfig, sys.argv[1:])
        print(f"Hello, {config.name}!")
        if config.num is not None:
            print(f"Your number was: {config.num}")


Boolean flags
'''''''''''''
Boolean config attributes result in a flag which takes no value and defaults to ``False``. This is the equivalent of the ``store_true`` action in argparse.

.. code-block:: python

    import dataclasses
    import sys
    from cfgclasses import arg, parse_args

    @dataclasses.dataclass
    class MyConfig:
        """An example application with debug mode"""
        debug: bool

    if __name__ == "__main__":
        config = parse_args(MyConfig, sys.argv[1:])
        if config.debug:
            print("Debug mode enabled")
        print("Hello, world!")

.. code-block:: bash

    $ python example.py --help
    usage: example.py [-h] [--debug]

    options:
      -h, --help   show this help message and exit

      --debug

    $ python example.py
    Hello, world!

    $ python example.py --debug
    Debug mode enabled
    Hello, world!


Arguments with choices
''''''''''''''''''''''
Arguments can be restricted to a set of choices using the ``choices`` argument to ``arg``. This is the recommended way of interacting with enumerated types in python and for indexing into dictionaries.

.. code-block:: python

    import dataclasses
    import sys
    from cfgclasses import arg, parse_args

    COLOURS = {
        "red": "#ff0000",
        "green": "#00ff00",
        "blue": "#0000ff",
    }

    @dataclasses.dataclass
    class MyConfig:
        """An example application with debug mode"""
        colour: str = arg("Your favourite colour", choices=COLOURS)

    if __name__ == "__main__":
        config = parse_args(MyConfig, sys.argv[1:])
        print(f"Your favourite colour is {config.colour} which is {COLOURS[config.colour]}")

.. code-block:: bash

    $ python example.py --help
    usage: example.py [-h] --colour {red,green,blue}

    options:
      -h, --help            show this help message and exit

      --colour {red,green,blue}
                            Your favourite colour

    $ python example.py --colour red
    Your favourite colour is red which is #ff0000

    $ python example.py --colour orange
    usage: example.py [-h] --colour {red,green,blue}
    example.py: error: argument --colour: invalid choice: 'orange' (choose from 'red', 'green', 'blue')

Empty lists
'''''''''''
A configuration item that accepts a list of values will normally require at least one value to be passed. This can be avoided by using the ``default_factory`` argument to ``arg()`` to specify a factory function that returns an empty list. This use of ``default_factory`` is equivalent to ``default=[]``, except that it avoids re-use of the same list object across multiple instances of the class.

.. code-block:: python

    import dataclasses
    import sys
    from cfgclasses import arg, parse_args

    @dataclasses.dataclass
    class MyConfig:
        """An example application with debug mode"""
        required: list[str] = arg("A required list of strings")
        optional: list[str] = arg("An optional list of strings", default_factory=list)

    if __name__ == "__main__":
        config = parse_args(MyConfig, sys.argv[1:])
        print(f"Required: {config.required}")
        print(f"Optional: {config.optional}")

.. code-block:: bash

    $ python example.py --help
    usage: foo.py [-h] --required REQUIRED [REQUIRED ...] [--optional OPTIONAL [OPTIONAL ...]]

    options:
      -h, --help            show this help message and exit

      --required REQUIRED [REQUIRED ...]
                            A required list of strings
      --optional OPTIONAL [OPTIONAL ...]
                            An optional list of strings

    $ python example.py --required A B C
    Required: ['A', 'B', 'C']
    Optional: []

    $ python example.py --required A --optional B C
    Required: ['A']
    Optional: ['B', 'C']
