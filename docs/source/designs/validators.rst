Validators
==========

1. Feature overview
-------------------

The validators feature allows the programmer to define a validation function that runs after the ConfigClass is initialized. The validation functions can raise ValueError's in cases of invalid configuration being specified which result in calls to ``argparse.ArgumentParser.error()`` result in nicely formatted errors for the user including the tools usage message and a non-zero exit code.

The default implementation of ``ConfigClass.validate()`` is a no-op and can be freely overriden by the programmer.

An example of the validators feature is shown below:

.. code-block::

    # price-checker.py

    import sys
    from cfgclasses import ConfigClass, choices, simple
    from dataclasses import dataclass

    ITEMS = {
        "shirt": {
            "red": 10.45,
            "green": 11.45,
            "orange": 12.60,
        },
        "socks": {
            "blue": 5.10,
            "green": 5.10,
        },
    }

    @dataclass
    class Config(ConfigClass):
        item: str = choices("Item to check the price for", ITEMS)
        # Note: we can't specify the choices for colour here because it depends
        # on the item
        colour: str = simple("Colour of the item")
        
        def validate(self):
            if self.colour not in ITEMS[self.item]:
                raise ValueError(f"{self.item} is not available in {self.colour}")

        def run(self):
            print(f"£{ITEMS[self.item][self.colour]}")
    
    if __name__ == '__main__':
        Config.parse_args(sys.argv[1:]).run()

Example runs:

.. code-block:: 

    $ python3 foo.py --item shirt --colour red
    £10.45

    $ price-checker.py --item shirt --colour blue
    usage: foo.py [-h] --item {shirt,socks} --colour COLOUR
    foo.py: error: shirt is not available in blue

2. Design ammendments
---------------------
The following additions are made to the primary design:
 * The ``ConfigClass`` class has a new method ``validate()`` which has a no-op implementation.
 * A new step is added to the high-level flow after creating the ``ConfigClass`` instance:

   * Invoke the ``validate()`` method for the top-level ``ConfigClass`` instance
   * Invoke the ``validate()`` method for each nested ``ConfigClass`` instance
   * If any ValueError's are raised by these methods, use the ``argparse.ArgumentParser.error()`` method to output the exception message.