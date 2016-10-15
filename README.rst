.......................
Simple Python GRASP API
.......................

Version: 0.1.4b (beta)

This module contains a Python 3 API to work with the GRASP database. The
database must be downloaded and initialized locally. The default is to use an
sqlite backend, but postgresql or mysql may be used also; these two are slower
to initialize (longer write times), but they may be faster on indexed reads.

The GRASP project is a SNP-level index of over 2000 GWAS datasets. It is very
useful, but difficult to batch query as study descriptions are heterogenous and
there are more than 9 million rows. By putting this information into a relational
database, it is easy to pull out bite-sized chunks of data to analyze with
`pandas <http://pandas.pydata.org/>`_.

Commonly queried columns are indexed within the database for fast retrieval. A typical
query for a single phenotype category returns several million SNPs in about 10 seconds,
which can then be analyzed with pandas.

To read more about GRASP, visit the `official page <https://grasp.nhlbi.nih.gov/Overview.aspx>`_.

For reference information (e.g. column, population, and phenotype lists) see
`the wiki <https://github.com/MikeDacre/grasp/wiki>`_.

For complete API documentation, go to the
`documentation site <https://mikedacre.github.io/grasp/>`_

.. contents:: **Contents**

============
Installation
============

Use the standard installation procedure:

.. code:: shell

  git clone https://github.com/MikeDacre/grasp.git
  cd grasp
  python ./setup.py install --user

This code requires a grasp database. Currently sqlite/postgesql/mysql are
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

=====
Usage
=====

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

Table Contents
==============

This module provides 6 tables:

`Study <https://github.com/MikeDacre/grasp/wiki/Table-Columns#study>`_,
`Phenotype <https://github.com/MikeDacre/grasp/wiki/Table-Columns#phenotype>`_,
`PhenoCats <https://github.com/MikeDacre/grasp/wiki/Table-Columns#phenocats`_,
`Platform <https://github.com/MikeDacre/grasp/wiki/Table-Columns#platform>`_,
`Population <https://github.com/MikeDacre/grasp/wiki/Table-Columns#population`_,
and `SNP <https://github.com/MikeDacre/grasp/wiki/Table-Columns#snp`_ (as well
as several association tables)

Querying
========

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

Example Usage
=============

.. code:: python

  from grasp import db
  from grasp import tables as t
  from grasp import query as q
  s, e = db.get_session()

  # Print a list of all phenotypes (also use with populations, but not with SNPs (too many to display))
  s.query(t.Phenotype).all()

  # Get a disease
  t2d = s.query(t.Phenotype).filter(t.Phenotype.category == "Type 2 diabetes (T2D)").first()

  len(t2d.snps)  # Outputs 785386

  # Get a single population
  eur = s.query(t.Population).filter(t.Population.population == 'European').first()

  # An example workflow
  eur_t2d_studies = [i for i in t2d.studies if i.population.population == 'European']

  eur_t2d_studies

  Out[11]:
  [22293688 <Huang:Eur J Hum Genet "Multiple traits (bipolar disorder, coronary artery disease, Crohn's disease, rheumatoid arthritis, T1D, T2D, hypertension)" EUR: 16179, AFR: None>,
   22399527 <Kristiansson:Circ Cardiovasc Genet "Metabolic syndrome (HDL cholesterol, triglycerides, plasma glucose, waist circumference, systolic and diastolic blood pressure)" EUR: 10564, AFR: None>,
   22581228 <Manning:Nat Genet Fasting glycemic traits and insulin resistance EUR: 58074, AFR: None>,
   22693455 <Perry:PLoS Genet Type II Diabetes Mellitus EUR: 60647, AFR: None>,
   22885924 <Scott:Nat Genet "Fasting glucose and insulin, and response to glucose in plasma" EUR: 133010, AFR: None>,
   23054467 <Postula:J Thromb Thrombolysis Platelet reactivity in patients with type 2 diabetes during acetylsalicylic acid (ASA) treatment EUR: 289, AFR: None>,
   23263489 <Huyghe:Nat Genet Fasting insulin processing and secretion in non-diabetics EUR: 8229, AFR: None>,
   23565322 <Raynor:Int J Mol Epidemiol Genet Type II Diabetes Mellitus and prostate cancer EUR: 7644, AFR: None>,
   23674605 <t Hart:Diabetes Response to glucose and GLP-1-infusion on insulin secretion EUR: 232, AFR: None>,
   17293876 <Sladek:Nature Type II Diabetes Mellitus EUR: 1275, AFR: None>,
   17460697 <Steinthorsdottir:Nat Genet Type II Diabetes Mellitus EUR: 6674, AFR: None>,
   17463246 <Broad DGI Webtables:Science "Multiple traits (lipids, glucose, obesity, blood pressure)" EUR: 5217, AFR: None>,
   17463248 <Scott:Science Type II Diabetes Mellitus EUR: 2335, AFR: None>,
   17463249 <Zeggini:Science Type II Diabetes Mellitus EUR: 4862, AFR: None>,
   17554300 <WTCCC:Nature "Multiple traits (bipolar disorder, coronary artery disease, Crohn's disease, rheumatoid arthritis, T1D, T2D, hypertension)" EUR: 4806, AFR: None>,
   17668382 <Salonen:Am J Hum Genet Type II Diabetes Mellitus EUR: 997, AFR: None>,
   17903298 <Meigs:BMC Med Genet Type II Diabetes Mellitus EUR: 1087, AFR: None>,
   18372903 <Zeggini E:Nat Genet Type II Diabetes Mellitus EUR: 10128, AFR: None>,
   18451265 <Bouatia-Naji N:Science "Fasting glucose, in plasma" EUR: 654, AFR: None>,
   18521185 <Chen WM:J Clin Invest Fasting glucose EUR: 5088, AFR: None>,
   19056611 <Timpson NJ:Diabetes Type II Diabetes Mellitus EUR: 4862, AFR: None>,
   19060907 <Prokopenko I:Nat Genet Fasting glucose EUR: 35812, AFR: None>,
   19060909 <Bouatia-Naji N:Nat Genet "Fasting glucose, in plasma" EUR: 2151, AFR: None>,
   19184112 <BossAC Y:Hum Genet Type II Diabetes Mellitus EUR: 1235, AFR: None>,
   19734900 <Rung:Nat Genet Type II Diabetes Mellitus EUR: 1376, AFR: None>,
   20081857 <Saxena:Nat Genet Response to glucose and insulin EUR: 15234, AFR: None>,
   20081858 <Dupuis:Nat Genet "Glucose homeostasis traits (fasting glucose, fasting insulin, HOMA-B, HOMA-IR)" EUR: 46186, AFR: None>,
   20418489 <Qi:Hum Mol Genet Type II Diabetes Mellitus EUR: 5643, AFR: None>,
   20581827 <Voight:Nat Genet Type II Diabetes Mellitus EUR: 47117, AFR: None>,
   20628086 <Bailey:Diabetes Care Thiazolidinedione-induced edema EUR: 1921, AFR: None>,
   21186350 <Zhou:Nat Genet Response to metformin EUR: 1024, AFR: None>,
   21386085 <Kraja:Diabetes "Metabolic syndrome (waist circumference, fasting glucose, HDL cholesterol, triglycerides, blood pressure)" EUR: 22161, AFR: None>,
   21873549 <Strawbridge:Diabetes Fasting proinsulin levels in non-diabetics EUR: 10701, AFR: None>]

  # These should obviously be filtered more to be useful

  # Now we have a list of studies, we can get the SNPs from them directly, but that isn't efficient.
  # Instead, we will use their IDs and get a dataframe directly
  # We will limit the size of the dataframe in memory to make it easier to work with

  import pandas as pd
  eur_t2d_snps = pd.read_sql(s.query(t.SNP.id, t.SNP.chrom, t.SNP.pos, t.SNP.pval).filter(t.SNP.study_id.in_([i.id for i in t2d.studies if i.population.population == "European"])).statement, e, index_col='id')
  afr_t2d_snps = pd.read_sql(s.query(t.SNP.id, t.SNP.chrom, t.SNP.pos, t.SNP.pval).filter(t.SNP.study_id.in_([i.id for i in t2d.studies if i.population.population == "African"])).statement, e, index_col='id')

  # SNP dataframe creation can be shortcut with the q.get_pheno_pop_snps function
  eur_t2d_snps = q.get_pheno_pop_snps(pheno="Type 2 diabetes (T2D)", pop="European", pandas=True)
  afr_t2d_snps = q.get_pheno_pop_snps(pheno=[afr_t2d_studies], pandas=True)
  # afr_t2d_studies is a filtered list of studies containing only the studies you want

  # Filter both by pval
  eur_t2d_snps = eur_t2d_snps[eur_t2d_snps.pval < 1e-8]
  afr_t2d_snps = afr_t2d_snps[eur_t2d_snps.pval < 1e-8]

====
ToDo
====

 - Add more functions to grasp script, including lookup by position or range of positions
