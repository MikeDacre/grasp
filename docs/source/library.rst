Library (API Documentation)
===========================

This code is intended to be primarily used as a library, and works best when
used in an interactive python session (e.g. with jupyter) alongside pandas.
Many of the query functions in this library returns pandas dataframes.

Below is a complete documentation of the API for this library. The functions in
`grasp.query` will be the most interesting for most users wanting to do common
db queries.

Tables are defined in `grasp.tables`, functions for connecting to and building
the database are in `grasp.db`. `grasp.info` contains simple documentation for
all of the tables and phenotypes (used to build this documentation).

`grasp.config` handles the static database configuration at `~/.grasp`, and
`grasp.ref` is used to define module wide static objects, like dictionaries
and the `PopFlags` class.


grasp.query
-----------

.. automodule:: grasp.query
    :show-inheritance:

get_studies
...........

.. autofunction:: grasp.query.get_studies
   :show-inheritance:

get_snps
........

.. autofunction:: grasp.query.get_snps
   :show-inheritance:

lookup_rsid
...........

.. autofunction:: grasp.query.lookup_rsid
   :show-inheritance:

lookup_location
...............

.. autofunction:: grasp.query.lookup_location
   :show-inheritance:

lookup_studies
..............

.. autofunction:: grasp.query.lookup_studies
   :show-inheritance:

get_variant_info
................

.. autofunction:: grasp.query.get_variant_info
   :show-inheritance:
 
get_collapse_dataframe
......................

.. autofunction:: grasp.query.collapse_dataframe
   :show-inheritance:

intersect_overlapping_series
............................

.. autofunction:: grasp.query.intersect_overlapping_series
   :show-inheritance:


write_study_dict
................

.. autofunction:: grasp.query.write_study_dict
   :show-inheritance:

grasp.tables
------------

.. automodule:: grasp.tables
    :show-inheritance:

SNP
...

.. autoclass:: grasp.tables.SNP
   :members:
   :show-inheritance:

Study
.....

.. autoclass:: grasp.tables.Study
   :members:
   :show-inheritance:

Phenotype
.........

.. autoclass:: grasp.tables.Phenotype
   :members:
   :show-inheritance:

PhenoCats
.........

.. autoclass:: grasp.tables.Phenotype
   :members:
   :show-inheritance:

Population
...........

.. autoclass:: grasp.tables.Population
   :members:
   :show-inheritance:

Platform
........

.. autoclass:: grasp.tables.Platform
   :members:
   :show-inheritance:

grasp.db
--------

.. automodule:: grasp.db
    :members:
    :undoc-members:
    :show-inheritance:


grasp.config
------------

.. automodule:: grasp.config
    :members:
    :undoc-members:
    :show-inheritance:

grasp.info
----------

.. automodule:: grasp.info
    :members:
    :undoc-members:
    :show-inheritance:
 
grasp.ref
---------

`ref.py` holds some simple lookups and the `PopFlags` classes that don't really
go anywhere else.

.. automodule:: grasp.ref
    :members:
    :undoc-members:
    :show-inheritance:
