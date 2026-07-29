.. image:: https://img.shields.io/pypi/v/earthkit-data-meteoswiss-opendata.svg
    :target: https://pypi.org/project/earthkit-data-meteoswiss-opendata/

.. image:: https://img.shields.io/badge/documentation-latest-blue.svg
    :target: https://meteoswiss.github.io/earthkit-data-meteoswiss-opendata/
    :alt: Documentation

.. image:: https://img.shields.io/pypi/pyversions/earthkit-data-meteoswiss-opendata.svg
    :target: https://pypi.org/project/earthkit-data-meteoswiss-opendata/

.. image:: https://img.shields.io/pypi/l/earthkit-data-meteoswiss-opendata.svg
    :target: https://pypi.org/project/earthkit-data-meteoswiss-opendata/

.. image:: https://github.com/MeteoSwiss/earthkit-data-meteoswiss-opendata/actions/workflows/CI_test.yaml/badge.svg
    :target: https://github.com/MeteoSwiss/earthkit-data-meteoswiss-opendata/actions/workflows/CI_test.yaml

.. image:: https://github.com/MeteoSwiss/earthkit-data-meteoswiss-opendata/actions/workflows/CI_publish_dev_documentation.yaml/badge.svg
    :target: https://github.com/MeteoSwiss/earthkit-data-meteoswiss-opendata/actions/workflows/CI_publish_dev_documentation.yaml

===============
Getting Started
===============

``earthkit-data-meteoswiss-opendata`` provides earthkit-data source plugins for accessing MeteoSwiss numerical weather prediction data through the MeteoSwiss Open Data STAC API.

Installation
------------

Install the released package with pip:

.. code-block:: console

    $ pip install earthkit-data-meteoswiss-opendata

With Poetry:

.. code-block:: console

    $ poetry add earthkit-data-meteoswiss-opendata

Installing the package also installs ``earthkit-data`` and automatically
registers the ``meteoswiss-opendata`` and
``meteoswiss-opendata-constants`` source plugins. No additional plugin
configuration is required.

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

    dataset = forecast.to_xarray(time_dims=["forecast_reference_time", "step"], squeeze=False)
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

Model Constants
---------------

Load the horizontal or vertical constants associated with a model collection:

.. code-block:: python

    horizontal = ekd.from_source(
        "meteoswiss-opendata-constants",
        collection="ogd-forecasting-icon-ch2",
        asset="horizontal",
    )

    vertical = ekd.from_source(
        "meteoswiss-opendata-constants",
        collection="ogd-forecasting-icon-ch2",
        asset="vertical",
    )

The ``asset`` parameter accepts ``"horizontal"`` or ``"vertical"``. The
returned data can be handled with the standard earthkit methods e.g. `to_xarray() <https://earthkit-data.readthedocs.io/en/latest/autoapi/earthkit/data/indexing/xarray/index.html#earthkit.data.indexing.xarray.XarrayMixIn.to_xarray>`__ or `to_target() <https://earthkit-data.readthedocs.io/en/latest/concepts/targets/to_target.html#to_target>`__, for example:

.. code-block:: python

    horizontal.to_target(
        "file",
        "horizontal_constants_icon-ch2-eps.grib2",
    )

Related Links
-------------

* `Plugin documentation <https://meteoswiss.github.io/earthkit-data-meteoswiss-opendata/>`__
* `earthkit-data documentation <https://earthkit-data.readthedocs.io/en/latest/>`__
* `earthkit source plugin documentation <https://earthkit-data.readthedocs.io/en/latest/concepts/plugins/sources_plugin.html>`__
* `MeteoSwiss Open Data documentation <https://opendatadocs.meteoswiss.ch/>`__
* `MeteoSwiss numerical weather prediction data <https://opendatadocs.meteoswiss.ch/e-forecast-data>`__
* `MeteoSwiss constant parameters example <https://github.com/MeteoSwiss/opendata-nwp-demos/blob/main/09_constant_parameters.ipynb>`__
* `MeteoSwiss Open Data NWP example notebooks <https://github.com/MeteoSwiss/opendata-nwp-demos>`__

Collection Browser
''''''''''''''''''

The available collection assets can be inspected in the STAC Browser:

* `ICON-CH1-EPS collection <https://data.geo.admin.ch/browser/index.html#/collections/ch.meteoschweiz.ogd-forecasting-icon-ch1>`__
* `ICON-CH2-EPS collection <https://data.geo.admin.ch/browser/index.html#/collections/ch.meteoschweiz.ogd-forecasting-icon-ch2>`__
* `KENDA-CH1 collection <https://data.geo.admin.ch/browser/index.html#/collections/ch.meteoschweiz.ogd-analysis-kenda-ch1>`__

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
