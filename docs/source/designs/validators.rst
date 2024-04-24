Validators
==========

1. Feature overview
-------------------

The validators feature allows the programmer to define a validation function that runs after the dataclass is initialized from CLI arguments. The validation functions can raise ValueError's in cases of invalid configuration being specified which result in calls to ``argparse.ArgumentParser.error()`` result in nicely formatted errors for the user including the tools usage message and a non-zero exit code.

An example of the validators feature is shown below:

.. code-block:: python

    # price-checker.py

    import sys
    from cfgclasses import arg, parse_args, validator
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
    class Config:
        item: str = arg("Item to check the price for", choices=ITEMS)
        # Note: we can't specify the choices for colour here because it depends
        # on the item
        colour: str = arg("Colour of the item")
        
        @validator
        def validate_available_color(self):
            if self.colour not in ITEMS[self.item]:
                raise ValueError(f"{self.item} is not available in {self.colour}")

        def run(self):
            print(f"£{ITEMS[self.item][self.colour]}")
    
    if __name__ == '__main__':
        parse_args(Config, sys.argv[1:]).run()

Example runs:

.. code-block:: bash

    $ python3 foo.py --item shirt --colour red
    £10.45

    $ price-checker.py --item shirt --colour blue
    usage: foo.py [-h] --item {shirt,socks} --colour COLOUR
    foo.py: error: shirt is not available in blue

2. Design ammendments
---------------------
The following additions are made to the primary design:
 * A new ``@validator`` decorator is added to the ``cfgclasses`` module which accepts a single argument, the validation function.
   * The decorator sets a marker attribute on the validation function to indicate that it is a cfgclasses validator.
 * A new step is added to the high-level flow after creating the ``dataclass`` instance:
   * Check all attributes of the instance (exclusing those starting ``__``)
   * If the attribute has a marker attribute indicating it is a validator, call the attribute.
   * Repeat this process for all nested ``dataclass`` instances.
   * If any ValueError's are raised by these methods, use the ``argparse.ArgumentParser.error()`` method to output the exception message.
