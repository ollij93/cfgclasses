Submodes
========

1. Problem Definition
---------------------
Tools can have submodes that accept different groups of argument. 

For example, the ``git`` command has a ``git commit`` submode and a ``git add`` submode etc. Each of these submodes accepts different arguments, but there are also some core options that are common to all submodes.

``cfgclasses.ConfigClass`` provides a ``parse_args_with_submodes()`` classmethod that can be used for tools with this setup. The common options which apply to all submodes are defined in the ``ConfigClass`` subclass whose ``parse_args_with_submodes()`` method is invoked, and the submode-specific options are defined in separate ``ConfigClass`` subclasses for each submode. This classmethod than returns both an instance of the common options ``ConfigClass``  and an instance of the submode-specific options ``ConfigClass``.

2. Design Ammendments
---------------------
The ``parse_args_with_submodes()`` classmethod is added to the ``ConfigClass`` definition. This functions signature is:

.. code-block:: python

    def parse_args_with_submodes(
        cls: Type[_T],
        argv: Sequence[str],
        submodes: dict[str, Type[_U]],
        prog: Optional[str] = None,
    ) -> tuple[_T, _U]:

Where ``_T`` is a type variable that is bound to the ``ConfigClass`` subclass that is invoking the method, and ``_U`` is a type variable that is bound to the ``ConfigClass`` subclass for the submodes. The latter allows the submodes of the user to all inherit from a common base-type which can be beneficial for including methods on the configuration. For example, the Author likes to include a ``run()`` method on the configuration class to act as the main method of the tool. This method can be defined on the base-type and then overriden by all submodes to perform their custom flow for the appropriate submode.

The flow of this function follows the same flow as for the simpler ``parse_args()`` with the following additions:
 * The ``argparse.ArgumentParser.add_subparsers()`` method is used to add a new subparser for each submode with the appropriate name.
 * After the top-level ``ConfigClass`` has created its specification and added them to the parser, the same is done for each submode ``ConfigClass``, adding the arguments to the appropriate subparser.
 * Once the arguments have been parsed into the ``argparse.Namespace``, the submode is checked and an error raised if it is unselected.
 * The creation of the two ``ConfigClass`` instances is then performed as normal.
 * Validation is performed on both the top-level and submode ``ConfigClass`` instances.
