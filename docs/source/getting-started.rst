Getting Started
===============

This page will guide you through getting started with a simple python
application using cfgclasses to define the command line interface.
For more details on the features of cfgclasses, see the :doc:`api` documentation.

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
    from cfgclasses import ConfigClass, arg

    @dataclasses.dataclass
    class MyConfig(ConfigClass):
        """A simple example application"""
        name: str = arg("Your name")
        num: int = arg("An integer option", default=0)

    if __name__ == "__main__":
        config = MyConfig.parse_args(sys.argv[1:])
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

cfgclasses comes with a number of utilty methods to reduce the volume of code
required to define an applications interface. The most common of these has
already been seen in the example above: ``arg(helpstr)``.

@@@ TODO @@@ TODO
