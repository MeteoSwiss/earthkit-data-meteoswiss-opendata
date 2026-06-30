.. image:: https://img.shields.io/pypi/v/earthkit-data-meteoswiss-opendata.svg
    :target: https://pypi.org/project/earthkit-data-meteoswiss-opendata/

.. image:: https://img.shields.io/pypi/pyversions/earthkit-data-meteoswiss-opendata.svg
    :target: https://pypi.org/project/earthkit-data-meteoswiss-opendata/

.. image:: https://img.shields.io/pypi/l/earthkit-data-meteoswiss-opendata.svg
    :target: https://pypi.org/project/earthkit-data-meteoswiss-opendata/

.. image:: https://github.com/MeteoSwiss/earthkit-data-meteoswiss-opendata/actions/workflows/github-code-scanning/codeql/badge.svg
    :target: https://github.com/MeteoSwiss/earthkit-data-meteoswiss-opendata/actions/workflows/github-code-scanning/codeql

.. image:: https://github.com/MeteoSwiss/earthkit-data-meteoswiss-opendata/actions/workflows/CI_test.yaml/badge.svg
    :target: https://github.com/MeteoSwiss/earthkit-data-meteoswiss-opendata/actions/workflows/CI_test.yaml

.. image:: https://github.com/MeteoSwiss/earthkit-data-meteoswiss-opendata/actions/workflows/CI_publish_dev_documentation.yaml/badge.svg
    :target: https://github.com/MeteoSwiss/earthkit-data-meteoswiss-opendata/actions/workflows/CI_publish_dev_documentation.yaml

===============
Getting Started
===============

Earthkit-data plugin for accessing NWP MeteoSwiss Open Data.




Development Setup with Poetry
-----------------------------

Building the Project
''''''''''''''''''''
.. code-block:: console

    $ cd earthkit-data-meteoswiss-opendata
    $ poetry install

Run Tests
'''''''''

.. code-block:: console

    $ poetry run pytest

Run Quality Tools
'''''''''''''''''

.. code-block:: console

    $ poetry run pylint earthkit_data_meteoswiss_opendata
    $ poetry run mypy earthkit_data_meteoswiss_opendata
    $ poetry run ruff format

Generate Documentation
''''''''''''''''''''''

.. code-block:: console

    $ poetry run sphinx-build doc doc/_build

Then open the index.html file generated in *earthkit-data-meteoswiss-opendata/doc/_build/*.

Build wheels
''''''''''''

.. code-block:: console

    $ poetry build

Using the Library
-----------------

To install earthkit-data-meteoswiss-opendata in your project, run this command in your terminal:

.. code-block:: console

    $ poetry add earthkit-data-meteoswiss-opendata

You can then use the library in your project through

    import earthkit_data_meteoswiss_opendata

Release the Project
-------------------

The project follows the **GitOps concept**: releases are triggered whenever a Git TAG is created.

The TAG must follow the `semantic version <https://semver.org/>`__ format and `PEP 440 <https://peps.python.org/pep-0440/>`__ , otherwise the release task will fail.

Follow these steps to create a new release:

* Adapt CHANGELOG.rst with release information
* Adapt ``doc/_static/switcher_config.json`` adding the new documentation URL for the release
* Create a new Release in the Github project
