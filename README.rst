Simple Python GRASP API
=======================

+---------+-------------------------------------------------+
| Author  | Michael D Dacre <mike.dacre@gmail.com>          |
+---------+-------------------------------------------------+
| License | MIT License, made at Stanford, use as you wish. |
+---------+-------------------------------------------------+
| Version | 0.4.0b1                                         |
+---------+-------------------------------------------------+


.. image:: https://api.codacy.com/project/badge/Grade/6a6be14b83894d76b440e853ff7e5cd3
   :target: https://www.codacy.com/app/mike-dacre/grasp?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=MikeDacre/grasp&amp;utm_campaign=Badge_Grade
.. image:: https://readthedocs.org/projects/grasp/badge/?version=latest
   :target: https://grasp.readthedocs.io/
.. image:: https://img.shields.io/badge/python%20versions-3.4%203.5%203.6-brightgreen.svg


This module contains a Python 3 API to work with the GRASP database. The
database must be downloaded and initialized locally. The default is to use an
sqlite backend, but postgresql or mysql may be used also; these two are slower
to initialize (longer write times), but they may be faster on indexed reads.

The GRASP project is a SNP-level index of over 2000 GWAS datasets. It is very
useful, but difficult to batch query as study descriptions are heterogeneous and
there are more than 9 million rows. By putting this information into a relational
database, it is easy to pull out bite-sized chunks of data to analyze with
`pandas <http://pandas.pydata.org/>`_. Be aware that GRASP does not include all
of the SNPs that they should (see               
`the wiki <https://github.com/MikeDacre/grasp/wiki>`_ for info), so use this
software with caution.

Commonly queried columns are indexed within the database for fast retrieval. A typical
query for a single phenotype category returns several million SNPs in about 10 seconds,
which can then be analyzed with pandas.

To read more about GRASP, visit the `official page <https://grasp.nhlbi.nih.gov/Overview.aspx>`_.

For a community discussion of the data itself see               
`the wiki <https://github.com/MikeDacre/grasp/wiki>`_. This contains some important
disclaimers regarding the quality of the data in GRASP itself, that fundamentally
limit the utility of this package.

For complete API documentation, go to the
`documentation site <https://grasp.readthedocs.io/en/latest/>`_

For a nice little example of usage, see the `BMI Jupyter Notebook
<https://github.com/MikeDacre/grasp/blob/master/examples/BMI_EUR_v_AFR.ipynb>`_

.. contents:: **Contents**

Installation
------------

The best way to install is with pip:

.. code:: shell

   pip install https://github.com/MikeDacre/grasp/archive/v0.4.0b1.tar.gz

When this code reaches version 0.4.1, it will be placed on pypi.

Alternatively, you can clone the repo and install with setuptools:

.. code:: shell

  git clone https://github.com/MikeDacre/grasp.git
  cd grasp
  python ./setup.py install --user

This code requires a grasp database. Currently sqlite/postgresql/mysql are
supported. Mysql and postgresql can be remote (but must be set up with this
tool), sqlite is local.

Database configuration is stored in a config file that lives by default in
~/.grasp.  This path is set in `config.py` and can be changed there is needed.

A script, `grasp`, is provided in `bin` and should automatically be installed
to your `PATH`.  It contains functions to set up your database config and to
initialize the grasp database easily, making the initial steps trivial.

To set up your database configuration, run:

.. code:: shell

  grasp config --init

This will prompt you for your database config options and create a file at
`~/.grasp` with those options saved.

You can now initialize the grasp database:

.. code:: shell

   grasp init study_file grasp_file

The study file is available in this repository (`grasp2_studies.txt.gz <https://raw.githubusercontent.com/MikeDacre/grasp/master/grasp2_studies.txt.gz>`_)
It is just a copy of the official `GRASP List of Studies <https://grasp.nhlbi.nih.gov/downloads/GRASP2_List_Of_Studies.xlsx>`_
converted to text and with an additional index that provides a numeric index
for the non pubmed indexed studies.

Both files can be gzipped or bzipped.

The grasp file is the raw unzipped file from the project page:
`GRASP2fullDataset <https://s3.amazonaws.com/NHLBI_Public/GRASP/GraspFullDataset2.zip>`_

The database takes about 90 minutes to build on a desktop machine and uses
about 3GB of space. The majority of the build time is spent parsing dates,
but because the dates are encoded in the SNP table, and the formatting varies,
this step is required.

Usage
-----

The code is based on SQLAlchemy, so you should read their `ORM Query tutorial <http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#querying>`_
to know how to use this well.

It is important to note that the point of this software is to make bulk data access from the GRASP
DB easy, SQLAlchemy makes this very easy indeed. However, to do complex comparisons,
SQLAlchemy is very slow. As such, the best way to use this software is to use
SQLAlchemy functions to bulk retrieve study lists, and then to directly get
a pandas dataframe of SNPs from those lists.

Tables are defined in `grasp.tables`
Database setup functions are in `grasp.db`
Query tools for easy data manipulation are in `grasp.query`.

Tables
......

This module provides 6 tables:

`Study <http://grasp.readthedocs.io/en/latest/table_columns.html#study>`_,
`Phenotype <http://grasp.readthedocs.io/en/latest/table_columns.html#phenotype>`_,
`PhenoCats <http://grasp.readthedocs.io/en/latest/table_columns.html#phenocats>`_,
`Platform <http://grasp.readthedocs.io/en/latest/table_columns.html#platform>`_,
`Population <http://grasp.readthedocs.io/en/latest/table_columns.html#population>`_,
and `SNP <http://grasp.readthedocs.io/en/latest/table_columns.html#snp>`_ (as well
as several association tables)

Querying
........

The functions in `grasp.query` are very helpful in automating common queries.

The simplest way to get a dataframe from SQLAlchemy is like this:

.. code:: python

   df = pandas.read_sql(session.query(SNP).statement)

Note that if you use this exact query, the dataframe will be too big to be
useful. To get a much more useful dataframe:

.. code:: python

   studies = grasp.query.get_studies(pheno_cats='t2d', primary_pop='European')
   df = grasp.query.get_snps(studies)

It is important to note that there are **three** ways of getting
phenotype information:
- The Phenotype table, which lists the primary phenotype for every study
- The PhenoCats table, which lists the GRASP curated phenotype categories,
  each Study has several of these.
- The phenotype_desc column in the SNP table, this is a poorly curated
  column directly from the full dataset, it roughly corresponds to the
  information in the Phenotype table, but the correspondance is not exact
  due to an abundance of typos and slightly differently typed information.

Example Workflow
----------------

.. code:: python

  from grasp import db
  from grasp import tables as t
  from grasp import query as q
  s, e = db.get_session()

  # Print a list of all phenotypes (also use with populations, but not with SNPs (too many to display))
  s.query(t.Phenotype).all()

  # Filter the list
  s.query(t.Phenotype).filter(t.Phenotype.phenotype.like('%diabetes%').all()

  # Get a dictionary of studies to review
  eur_t2d = get_studies(only_disc_pop='eur', primary_phenotype='Type II Diabetes Mellitus', dictionary=True)

  # Filter those by using eur.pop() to remove unwanted studies, and then get the SNPs as a dataframe
  eur_snps_df = get_snps(eur, pandas=True)

  # Do the same thing for the african population
  afr_t2d = get_studies(only_disc_pop='afr', primary_phenotype='Type II Diabetes Mellitus', dictionary=True)
  afr.pop('Use of diverse electronic medical record systems to identify genetic risk for type 2 diabetes within a genome-wide association study.')
  afr_snps_df = get_snps(afr, pandas=True)

  # Collapse the matrices (take median of pvalue) and filter by resulting pvalue
  eur_snps_df = q.collapse_dataframe(eur_snps_df, mechanism='median', pvalue_filter=5e-8)
  afr_snps_df = q.collapse_dataframe(afr_snps_df, mechanism='median', pvalue_filter=5e-8)

  # The new dataframes are indexed by 'chr:pos'

  # Plot the overlapping SNPs
  snps = q.intersect_overlapping_series(eur_snps_df.pval_median, afr_snps_df.pval_median)
  snps.plot()

ToDo
----

* Add more functions to grasp script, including lookup by position or range of positions
