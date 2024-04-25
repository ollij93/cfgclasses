.. cfgclasses contribution documatation file

Contributing
============

If you would like to contribute to this project, please follow the following steps:

1. Fork this repository
2. Create a new branch for your feature or bugfix
3. Make your changes
4. Commit your changes
5. Push your changes to your fork
6. Create a pull request

Please make sure to follow the coding standards and conventions used throughout the project. Also, please make sure to write tests for your code.

Create a virtual environment
============================
Create a virtual environment and install the required dependencies using the following commands:

.. code-block:: bash

    $ python3 -m venv venv
    venv$ source venv/bin/activate
    venv$ pip install .[dependencies] .[dev-dependencies]

Running the tests
=================
Tests can be run using the following command:

.. code-block:: bash

    venv$ bin/run_tests.sh
    ======================================= test session starts =======================================
    platform darwin -- Python 3.10.4, pytest-7.4.2, pluggy-1.3.0
    rootdir: /Users/olijohns/cfgclasses
    plugins: anyio-4.3.0, mypy-testing-0.1.1
    collected 60 items

    cfgclasses/test/test_argspec.py ....................................                        [ 60%]
    cfgclasses/test/test_configclass.py ....                                                    [ 66%]
    cfgclasses/test/test_deprecated_api.py .....                                                [ 75%]
    cfgclasses/test/test_transforms.py ...                                                      [ 80%]
    cfgclasses/test/test_typing.py ............                                                 [100%]

    ======================================= 60 passed in 3.07s ========================================
    Wrote XML report to coverage.xml
    Name                                     Stmts   Miss  Cover   Missing
    ----------------------------------------------------------------------
    cfgclasses/__init__.py                       6      0   100%
    cfgclasses/arghelper.py                     58      1    98%   323
    cfgclasses/argspec.py                      162      3    98%   334, 348-349
    cfgclasses/configclass.py                   66      2    97%   88, 98
    cfgclasses/test/__init__.py                  0      0   100%
    cfgclasses/test/test_argspec.py             86      0   100%
    cfgclasses/test/test_configclass.py         59      0   100%
    cfgclasses/test/test_deprecated_api.py      61      0   100%
    cfgclasses/test/test_transforms.py          40      0   100%
    cfgclasses/test/test_typing.py              57      0   100%
    cfgclasses/transforms.py                    13      0   100%
    cfgclasses/validation.py                    29      0   100%
    ----------------------------------------------------------------------
    TOTAL                                      637      6    99%

Code coverage should be as close to 100% as possible. Only minor error flows are skipped in the current code.

Run the formatters linters
==========================
Linters can be run using the following command:

.. code-block:: bash

    venv$ bin/run_tools.sh
    All done! ✨ 🍰 ✨
    17 files left unchanged.
    Skipped 5 files
    Success: no issues found in 16 source files

    --------------------------------------------------------------------
    Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

Build the documentation
=======================
The documentation can be built using the following command:

.. code-block:: bash

    venv$ bin/build_docs.sh
    Running Sphinx v7.2.5
    loading pickled environment... done
    building [mo]: targets for 0 po files that are out of date
    writing output...
    building [html]: targets for 8 source files that are out of date
    updating environment: 1 added, 8 changed, 0 removed
    reading sources... [100%] index
    looking for now-outdated files... none found
    pickling environment... done
    checking consistency... done
    preparing documents... done
    copying assets... copying static files... done
    copying extra files... done
    done
    writing output... [100%] index
    generating indices... genindex py-modindex done
    writing additional pages... search done
    copying images... [100%] _static/icon.png
    dumping search index in English (code: en)... done
    dumping object inventory... done
    build succeeded.

    The HTML pages are in _build/html.

This can then be viewed locally by opening the `_build/html/index.html` file in a web browser.
E.g. with ``python3 -m http.server`` and navigating to http://localhost:8000/_build/html/index.html

Building the package for deployment
===================================
The package can be built and deployed to pypi using the following commands.

Be sure to bump the version number in ``pyproject.toml`` and ``docs/source/conf.py`` before release.
Similarly, be sure to tag the git commit for the release with the version number.

.. code-block:: bash

    venv$ python3 -m pip install --upgrade hatch twine pkginfo
    venv$ python3 -m build
    venv$ python3 -m twine upload --repository testpypi dist/* # To test the upload
    venv$ python3 -m twine upload dist/* # To upload to pypi
