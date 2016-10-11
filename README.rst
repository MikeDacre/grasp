.......................
Simple Python GRASP API
.......................

Version: 0.1 (alpha)

This module contains a Python 3 API to work with the GRASP database. The
database must be downloaded and initialized locally. The default is to use an
sqlite backend, but postgresql is more efficient.

The GRASP project is a SNP-level index of over 2000 GWAS datasets. It is very
useful, but difficult to batch query as study descriptions are heterogenous and
there are more than 9 million rows. By putting this information into a relational
database, it is easy to pull out bite-sized chunks of data to analyze with `pandas <http://pandas.pydata.org/>`_.

Commonly queried columns are indexed within the database for fast retrieval. A typical
query for a single phenotype category returns several million SNPs in about 10 seconds,
which can then be analyzed with pandas.

To read more about GRASP, visit the `official page <https://grasp.nhlbi.nih.gov/Overview.aspx>`_.

.. contents:: **Contents**

Installation
============

Use the standard installation procedure:

.. code:: shell

  git clone https://github.com/MikeDacre/grasp.git
  cd grasp
  python ./setup.py install --user

This code requires a local grasp database. You can choose to use sqlite or
postgresql/mysql as the backend. A script, `grasp`, is provided in `bin` and
should automatically be installed to your `PATH`. It makes these setup steps
easy.

To set up your database configuration, run:

.. code:: shell

  grasp config -i

This will prompt you for your database config options and create a file at
`~/.grasp` with those options saved.

You can now initialize the grasp database:

.. code:: shell

   grasp init study_file grasp_file

The study file is available in this repository (`grasp2_studies.txt <https://raw.githubusercontent.com/MikeDacre/grasp/master/grasp2_studies.txt>`_)
It is just a copy of the official `GRASP List of Studies <https://grasp.nhlbi.nih.gov/downloads/GRASP2_List_Of_Studies.xlsx>`_
converted to text and with an additional index that provides a numeric index for the non pubmed indexed studies.

The grasp file is the raw unzipped file from the project page:
`GRASP2fullDataset <https://s3.amazonaws.com/NHLBI_Public/GRASP/GraspFullDataset2.zip>`_

The database takes about 40 minutes to build on a desktop machine and uses about 2GB of space.

ToDo
====

 - Implement common queries with pandas
 - Include myvariant to make looking up additional SNP info easy
 - Add more functions to grasp script, including lookup by position or range of positions
