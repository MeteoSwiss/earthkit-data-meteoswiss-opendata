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

``earthkit-data-meteoswiss-opendata`` is an ``earthkit-data`` source plugin
for accessing MeteoSwiss numerical weather prediction data through the
MeteoSwiss Open Data STAC API.

Installation
------------

Install the released package with pip:

.. code-block:: console

    $ pip install earthkit-data-meteoswiss-opendata

With Poetry:

.. code-block:: console

    $ poetry add earthkit-data-meteoswiss-opendata

Installing the package registers the ``meteoswiss-opendata`` source with
``earthkit-data``. No change to ``earthkit-data`` itself is required.

Using the Library
-----------------

Load the latest deterministic ICON-CH2-EPS forecast +0h, +1h & +2h for total
precipitation:

.. code-block:: python

    import datetime as dt

    import earthkit.data as ekd

    forecast = ekd.from_source(
        "meteoswiss-opendata",
        collection="ogd-forecasting-icon-ch2",
        variable="TOT_PREC",
        perturbed=False,
        ref_time="latest",
        lead_time=[
            dt.timedelta(hours=0),
            dt.timedelta(hours=1),
            dt.timedelta(hours=2),
        ],
    )

    dataset = forecast.to_xarray(profile="grib")
    print(dataset)

For ``ref_time="latest"``, the plugin selects the newest forecast run that
contains all requested lead times.

An exact reference time can be provided as a timezone-aware
``datetime.datetime``:

.. code-block:: python

    forecast = ekd.from_source(
        "meteoswiss-opendata",
        collection="ogd-forecasting-icon-ch2",
        variable="TOT_PREC",
        perturbed=False,
        ref_time=dt.datetime(
            2026,
            7,
            20,
            6,
            tzinfo=dt.timezone.utc,
        ),
        lead_time=dt.timedelta(hours=1),
    )

ISO 8601 strings such as ``"2026-07-20T06:00:00Z"`` and ``"PT1H"`` are also
accepted.

Parameters
''''''''''

``collection``
    MeteoSwiss Open Data collection, for example
    ``ogd-forecasting-icon-ch2``.

``variable``
    Forecast variable name, for example ``TOT_PREC``.

``perturbed``
    ``False`` for deterministic data or ``True`` for perturbed data.

``ref_time``
    ``"latest"``, a timezone-aware ``datetime.datetime``, an ISO 8601
    datetime string, or an ISO 8601 datetime interval.

``lead_time``
    A ``datetime.timedelta``, an ISO 8601 duration string, or a list of
    either. Examples include ``datetime.timedelta(hours=1)``, ``"PT1H"``,
    and ``["PT0H", "PT1H", "PT2H"]``.

Development Setup with Poetry
-----------------------------

Building the Project
''''''''''''''''''''

.. code-block:: console

    $ cd earthkit-data-meteoswiss-opendata
    $ poetry install

Run Tests
'''''''''

Run the offline unit tests:

.. code-block:: console

    $ poetry run pytest

Run the optional live integration test:

.. code-block:: console

    $ RUN_INTEGRATION=1 poetry run pytest -m integration

Run Quality Tools
'''''''''''''''''

.. code-block:: console

    $ poetry run pylint earthkit_data_meteoswiss_opendata
    $ poetry run mypy earthkit_data_meteoswiss_opendata
    $ poetry run ruff format --check
    $ poetry run ruff check

Generate Documentation
''''''''''''''''''''''

.. code-block:: console

    $ poetry run sphinx-build doc doc/_build

Then open ``doc/_build/index.html``.

Build Wheels
''''''''''''

.. code-block:: console

    $ poetry build

Release the Project
-------------------

The project follows the **GitOps concept**: releases are triggered whenever a
Git tag is created.

The tag must follow `Semantic Versioning <https://semver.org/>`__ and
`PEP 440 <https://peps.python.org/pep-0440/>`__. Otherwise, the release task
will fail.

Follow these steps to create a release:

* Update ``CHANGELOG.rst`` with the release information.
* Update ``doc/_static/switcher_config.json`` with the new documentation URL.
* Create a new release and matching tag in the GitHub project.
