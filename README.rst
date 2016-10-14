.......................
Simple Python GRASP API
.......................

Version: 0.1.3a (alpha)

This module contains a Python 3 API to work with the GRASP database. The
database must be downloaded and initialized locally. The default is to use an
sqlite backend, but postgresql or mysql may be used also; these two are slower
to initialize (longer write times), but they may be faster on indexed reads.

The GRASP project is a SNP-level index of over 2000 GWAS datasets. It is very
useful, but difficult to batch query as study descriptions are heterogenous and
there are more than 9 million rows. By putting this information into a relational
database, it is easy to pull out bite-sized chunks of data to analyze with `pandas <http://pandas.pydata.org/>`_.

Commonly queried columns are indexed within the database for fast retrieval. A typical
query for a single phenotype category returns several million SNPs in about 10 seconds,
which can then be analyzed with pandas.

To read more about GRASP, visit the `official page <https://grasp.nhlbi.nih.gov/Overview.aspx>`_.

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

If you try to do SQLAlchemy intersect, join, or merge operations in order to get
SNP lists that way, you will find that it is very slow.

The simplest way to get a dataframe from SQLAlchemy is like this:

.. code:: python

   df = pandas.read_sql(session.query(SNP).statement)

Note that if you use this exact query, the dataframe will be too big to be
useful, this is just an example of syntax. All of the functions in grasp.query
provide ways to get dataframes back from grasp with ease. `get_snps()`
(described below) is the best example of this.

This module provides 5 tables:

Study, Phenotype, PhenoCats, Platform, and SNP (as well as several association tables)

It is important to note that there are **three** ways of getting
phenotype information:
- The Phenotype table, which lists the primary phenotype for every study
- The PhenoCats table, which lists the GRASP curated phenotype categories,
  each Study has several of these.
- The phenotype_desc column in the SNP table, this is a poorly curated
  column directly from the full dataset, it roughly corresponds to the
  information in the Phenotype table, but the correspondance is not exact
  due to an abundance of typos and slightly differently typed information.

Tables are defined in grasp.tables
Database setup functions are in grasp.db
Query tools for easy data manipulation are in grasp.query.

Simple usage:

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
  

Columns
=======

It helps to know beforehand the relevant phenotypes, populations and columns, so here they are:

Phenotypes
----------
- 
- Asthma
- Pulmonary
- Chronic lung disease
- Inflammation
- Quantitative trait(s)
- Gene expression (protein)
- Protein expression
- Blood-related
- Cell line
- Cancer
- Endometrial cancer
- Reproductive
- Gender
- Female
- Treatment response
- Physical activity
- Eye-related
- Type 2 diabetes (T2D)
- Gene expression (RNA)
- Neuro
- Methylation
- Epigenetics
- Behavioral
- Bipolar disorder
- Breast cancer
- Drug response
- CVD risk factor (CVD RF)
- Lipids
- C-reactive protein (CRP)
- Serum
- Mortality
- Pregnancy-related
- Infection
- Tuberculosis
- HIV/AIDS
- Surgery
- Heart
- Cardiovascular disease (CVD)
- Myocardial infarction (MI)
- Thyroid cancer
- Thyroid
- Hormonal
- Developmental
- Aging
- Menopause
- Oral-related
- Bone-related
- Dental
- Adverse drug reaction (ADR)
- Immune-related
- Stroke
- Blood cancer
- Leukemia
- Lymphoma
- Systemic lupus erythematosus (SLE)
- Pancreatic cancer
- Pancreas
- Lung cancer
- Blood pressure
- Type 1 diabetes (T1D)
- Arthritis
- Rheumatoid arthritis
- "Crohns disease"
- Wound
- Gastrointestinal
- Colorectal cancer
- Gallbladder cancer
- Sleep
- Skin-related
- Esophageal cancer
- Nasal
- Anthropometric
- Imaging
- Weight
- Body mass index
- Plasma
- Subclinical CVD
- Male
- Prostate cancer
- Schizophrenia
- Addiction
- Smoking
- Epilepsy
- Adipose-related
- Urinary
- Cancer-related
- Environment
- "Huntingtons disease"
- Hepatic
- Social
- Renal
- Stone
- Muscle-related
- "Graves disease"
- Autism
- Congenital
- Glaucoma
- Platelet
- "Alzheimers disease"
- Diet-related
- "Parkinsons disease"
- Venous
- Thrombosis
- Depression
- Aneurysm
- Arterial
- Cognition
- Attention-deficit/hyperactivity disorder (ADHD)
- Multiple sclerosis (MS)
- Cystic fibrosis
- Brain cancer
- Amyotrophic lateral sclerosis (ALS)
- Chronic kidney disease
- Musculoskeletal
- Alcohol
- Vaccine
- Influenza
- Hepatitis
- Oral cancer
- Coronary heart disease (CHD)
- Smallpox
- Renal cancer
- Atrial fibrillation
- Hair
- Gallstones
- Sickle cell anemia
- Anemia
- Height
- miRNA
- Movement-related
- Anthrax
- Valve
- Age-related macular degeneration (ARMD)
- Menarche
- Ovarian cancer
- Liver cancer
- Vasculitis
- Ulcerative colitis
- Narcotics
- Chronic obstructive pulmonary disease (COPD)
- Salmonella
- Obsessive-compulsive disorder (OCD)
- Pain
- Radiation
- Allergy
- Myasthenia gravis
- Gastric cancer
- Hearing
- Heart rate
- Kidney cancer
- Nasal cancer
- Cardiomyopathy
- Bleeding disorder
- Hemophilia
- Calcium
- Skin cancer
- Melanoma
- Cervical cancer
- Rectal cancer
- Bone cancer
- Testicular cancer
- Celiac disease
- Heart failure
- Graft-versus-host
- Bladder cancer
- Mood disorder
- General health
- Emphysema
- Cytotoxicity
- T2D-related
- Treatment-related
- Upper airway tract cancer
- Uterine cancer
- Uterine fibroids
- Manic depression
- Basal cell cancer
- Blood
- CVD
- Drug treatment
- Allergy

Populations
============

- Hispanic
- European
- Mixed
- African
- Asian
- Unspecified
- Indian/South Asian
- Micronesian
- Arab/ME
- Native
- Filipino
- Indonesian

SNP Columns
===========

+--------------------+---------------------------------+
| Column             | Description                     |
+====================+=================================+
| ConservPredTFBS    | ConservPredTFBS                 |
+--------------------+---------------------------------+
| CreationDate       | CreationDate                    |
+--------------------+---------------------------------+
| EqtlMethMetabStudy | EqtlMethMetabStudy              |
+--------------------+---------------------------------+
| HUPfield           | HUPfield                        |
+--------------------+---------------------------------+
| HumanEnhancer      | HumanEnhancer                   |
+--------------------+---------------------------------+
| InGene             | InGene                          |
+--------------------+---------------------------------+
| InLincRNA          | InLincRNA                       |
+--------------------+---------------------------------+
| InMiRNA            | InMiRNA                         |
+--------------------+---------------------------------+
| InMiRNABS          | InMiRNABS                       |
+--------------------+---------------------------------+
| LSSNP              | LS-SNP                          |
+--------------------+---------------------------------+
| LastCurationDate   | LastCurationDate                |
+--------------------+---------------------------------+
| NHLBIkey           | NHLBIkey                        |
+--------------------+---------------------------------+
| NearestGene        | NearestGene                     |
+--------------------+---------------------------------+
| ORegAnno           | ORegAnno                        |
+--------------------+---------------------------------+
| PolyPhen2          | PolyPhen2                       |
+--------------------+---------------------------------+
| RNAedit            | RNAedit                         |
+--------------------+---------------------------------+
| SIFT               | SIFT                            |
+--------------------+---------------------------------+
| UniProt            | UniProt                         |
+--------------------+---------------------------------+
| chrom              | chr(hg19)                       |
+--------------------+---------------------------------+
| dbSNPClinStatus    | dbSNPClinStatus                 |
+--------------------+---------------------------------+
| dbSNPMAF           | dbSNPMAF                        |
+--------------------+---------------------------------+
| dbSNPfxn           | dbSNPfxn                        |
+--------------------+---------------------------------+
| dbSNPinfo          | dbSNPalleles/het/se             |
+--------------------+---------------------------------+
| dbSNPvalidation    | dbSNPvalidation                 |
+--------------------+---------------------------------+
| id                 | ID (generated from NHLBIKey)    |
+--------------------+---------------------------------+
| paper_loc          | LocationWithinPaper             |
+--------------------+---------------------------------+
| phenotypes         | Link to phenotypes              |
+--------------------+---------------------------------+
| population         | Link to population table        |
+--------------------+---------------------------------+
| population_id      | Primary key of population table |
+--------------------+---------------------------------+
| pos                | pos(hg19)                       |
+--------------------+---------------------------------+
| primary_pheno      | Phenotype                       |
+--------------------+---------------------------------+
| pval               | Pvalue                          |
+--------------------+---------------------------------+
| snpid              | SNPid(dbSNP134)                 |
+--------------------+---------------------------------+
| study              | Link to study table             |
+--------------------+---------------------------------+
| study_id           | Primary key of the study table  |
+--------------------+---------------------------------+

Study Columns
=============

+------------------+---------------------------------------------------------------------+
| Column           | Description                                                         |
+==================+=====================================================================+
| african          | African ancestry                                                    |
+------------------+---------------------------------------------------------------------+
| arab             | Arab/ME                                                             |
+------------------+---------------------------------------------------------------------+
| author           | 1st_author                                                          |
+------------------+---------------------------------------------------------------------+
| datepub          | DatePub                                                             |
+------------------+---------------------------------------------------------------------+
| east_asian       | East Asian                                                          |
+------------------+---------------------------------------------------------------------+
| european         | European                                                            |
+------------------+---------------------------------------------------------------------+
| filipino         | Filipino                                                            |
+------------------+---------------------------------------------------------------------+
| grasp_ver        | GRASPversion?                                                       |
+------------------+---------------------------------------------------------------------+
| hispanic         | Hispanic                                                            |
+------------------+---------------------------------------------------------------------+
| id               | ID                                                                  |
+------------------+---------------------------------------------------------------------+
| imputed          | From "Platform [SNPs passing QC]"                                   |
+------------------+---------------------------------------------------------------------+
| in_nhgri         | In NHGRI GWAS catalog (8/26/14)?                                    |
+------------------+---------------------------------------------------------------------+
| indonesian       | Indonesian                                                          |
+------------------+---------------------------------------------------------------------+
| journal          | Journal                                                             |
+------------------+---------------------------------------------------------------------+
| locations        | Specific place(s) mentioned for samples                             |
+------------------+---------------------------------------------------------------------+
| mf               | Includes male/female only analyses in discovery and/or replication? |
+------------------+---------------------------------------------------------------------+
| mf_only          | Exclusively male or female study?                                   |
+------------------+---------------------------------------------------------------------+
| micronesian      | Micronesian                                                         |
+------------------+---------------------------------------------------------------------+
| mixed            | Mixed                                                               |
+------------------+---------------------------------------------------------------------+
| native           | Native                                                              |
+------------------+---------------------------------------------------------------------+
| noresults        | No results flag                                                     |
+------------------+---------------------------------------------------------------------+
| pheno_desc       | Phenotype description                                               |
+------------------+---------------------------------------------------------------------+
| phenotypes       | Phenotype categories assigned                                       |
+------------------+---------------------------------------------------------------------+
| platforms        | Platform [SNPs passing QC]                                          |
+------------------+---------------------------------------------------------------------+
| pmid             | PubmedID                                                            |
+------------------+---------------------------------------------------------------------+
| population       | GWAS description link to table                                      |
+------------------+---------------------------------------------------------------------+
| population_id    | Primary key of population table                                     |
+------------------+---------------------------------------------------------------------+
| qtl              | IsEqtl/meQTL/pQTL/gQTL/Metabolmics?                                 |
+------------------+---------------------------------------------------------------------+
| rep_african      | African ancestry.1                                                  |
+------------------+---------------------------------------------------------------------+
| rep_arab         | Arab/ME.1                                                           |
+------------------+---------------------------------------------------------------------+
| rep_east_asian   | East Asian.1                                                        |
+------------------+---------------------------------------------------------------------+
| rep_european     | European.1                                                          |
+------------------+---------------------------------------------------------------------+
| rep_filipino     | Filipino.1                                                          |
+------------------+---------------------------------------------------------------------+
| rep_hispanic     | Hispanic.1                                                          |
+------------------+---------------------------------------------------------------------+
| rep_indonesian   | Indonesian.1                                                        |
+------------------+---------------------------------------------------------------------+
| rep_micronesian  | Micronesian.1                                                       |
+------------------+---------------------------------------------------------------------+
| rep_mixed        | Mixed.1                                                             |
+------------------+---------------------------------------------------------------------+
| rep_native       | Native.1                                                            |
+------------------+---------------------------------------------------------------------+
| rep_south_asian  | Indian/South Asian.1                                                |
+------------------+---------------------------------------------------------------------+
| rep_unpecified   | Unspec.1                                                            |
+------------------+---------------------------------------------------------------------+
| replication_size | Replication Sample Size                                             |
+------------------+---------------------------------------------------------------------+
| results          | #results                                                            |
+------------------+---------------------------------------------------------------------+
| sample_size      | Initial Sample Size                                                 |
+------------------+---------------------------------------------------------------------+
| snp_count        | From "Platform [SNPs passing QC]"                                   |
+------------------+---------------------------------------------------------------------+
| snps             | Link to all SNPs in this study                                      |
+------------------+---------------------------------------------------------------------+
| south_asian      | Indian/South Asian                                                  |
+------------------+---------------------------------------------------------------------+
| title            | Study                                                               |
+------------------+---------------------------------------------------------------------+
| total            | Total Discovery + Replication sample size                           |
+------------------+---------------------------------------------------------------------+
| total_disc       | Total discovery samples                                             |
+------------------+---------------------------------------------------------------------+
| total_rep        | Total replication samples                                           |
+------------------+---------------------------------------------------------------------+
| unpecified       | Unspec                                                              |
+------------------+---------------------------------------------------------------------+



ToDo
====

 - Implement common queries with pandas
 - Include myvariant to make looking up additional SNP info easy
 - Add more functions to grasp script, including lookup by position or range of positions
