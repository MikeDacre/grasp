"""
Holds reference objects for use elsewhere in the module.
"""
# Bitwise flags
from flags import Flags as _Flags

__all__ = ['PopFlag', 'pheno_synonyms']

###############################################################################
#                          Population Bitwise Flags                           #
###############################################################################


class PopFlag(_Flags):

    """A simplified bitwise flag system for tracking populations."""

    eur         = 1     #  European
    afr         = 2     #  African ancestry
    east_asian  = 4     #  East Asian
    south_asian = 8     #  Indian/South Asian
    his         = 16    #  Hispanic
    native      = 32    #  Native
    micro       = 64    #  Micronesian
    arab        = 128   #  Arab/ME
    mix         = 256   #  Mixed
    uns         = 512   #  Unspec
    filipino    = 1024  #  Filipino
    indonesian  = 2048  #  Indonesian


###############################################################################
#                              Correction Tables                              #
###############################################################################

pheno_synonyms = {
    'Allergy':                                         'allergy',
    'Addiction':                                       'addiction',
    'Adipose-related':                                 'adipose',
    'Adverse drug reaction (ADR)':                     'adr',
    'Age-related macular degeneration (ARMD)':         'armd',
    'Aging':                                           'aging',
    'Alcohol':                                         'alcohol',
    "Alzheimer's disease":                             'alzheimers',
    'Amyotrophic lateral sclerosis (ALS)':             'als',
    'Anemia':                                          'anemia',
    'Aneurysm':                                        'aneurysm',
    'Anthrax':                                         'anthrax',
    'Anthropometric':                                  'anthropometric',
    'Arterial':                                        'arterial',
    'Arthritis':                                       'arthritis',
    'Asthma':                                          'asthma',
    'Atrial fibrillation':                             'afib',
    'Attention-deficit/hyperactivity disorder (ADHD)': 'adhd',
    'Autism':                                          'autism',
    'Basal cell cancer':                               'basal_cell_cancer',
    'Behavioral':                                      'behavioral',
    'Bipolar disorder':                                'bipolar',
    'Bladder cancer':                                  'bladder_cancer',
    'Bleeding disorder':                               'bleeding_disorder',
    'Blood':                                           'blood',
    'Blood cancer':                                    'blood_cancer',
    'Blood pressure':                                  'bp',
    'Blood-related':                                   'blood',
    'Body mass index':                                 'bmi',
    'Bone cancer':                                     'bone_cancer',
    'Bone-related':                                    'bone',
    'Brain cancer':                                    'brain_cancer',
    'Breast cancer':                                   'breast_cancer',
    'C-reactive protein (CRP)':                        'crp',
    'CVD':                                             'cvd',
    'CVD risk factor (CVD RF)':                        'cvd_risk',
    'Calcium':                                         'calcium',
    'Cancer':                                          'cancer',
    'Cancer-related':                                  'cancer_related',
    'Cardiomyopathy':                                  'cardiomyopathy',
    'Cardiovascular disease (CVD)':                    'cvd',
    'Celiac disease':                                  'celiac',
    'Cell line':                                       'cell_line',
    'Cervical cancer':                                 'cervical_cancer',
    'Chronic kidney disease':                          'chronic_kidney_disease',
    'Chronic lung disease':                            'chronic_lung_disease',
    'Chronic obstructive pulmonary disease (COPD)':    'copd',
    'Cognition':                                       'cognition',
    'Colorectal cancer':                               'colorectal_cancer',
    'Congenital':                                      'congenital',
    'Coronary heart disease (CHD)':                    'chd',
    "Crohn's disease":                                 'crohns',
    'Cystic fibrosis':                                 'cf',
    'Cytotoxicity':                                    'cytotoxicity',
    'Dental':                                          'dental',
    'Depression':                                      'depression',
    'Developmental':                                   'developmental',
    'Diet-related':                                    'diet',
    'Drug response':                                   'drug_response',
    'Drug treatment':                                  'drug_treatment',
    'Emphysema':                                       'emphysema',
    'Endometrial cancer':                              'endometrial_cancer',
    'Environment':                                     'environment',
    'Epigenetics':                                     'epigenetics',
    'Epilepsy':                                        'epilepsy',
    'Esophageal cancer':                               'espohageal_cancer',
    'Eye-related':                                     'eye',
    'Female':                                          'female',
    'Gallbladder cancer':                              'gallbladder_cancer',
    'Gallstones':                                      'gallstones',
    'Gastric cancer':                                  'gastric_cancer',
    'Gastrointestinal':                                'gi',
    'Gender':                                          'gender',
    'Gene expression (RNA)':                           'rna_expression',
    'Gene expression (protein)':                       'gene_protein_expression',
    'General health':                                  'health',
    'Glaucoma':                                        'glaucoma',
    'Graft-versus-host':                               'graft_v_host',
    "Grave's disease":                                 'graves',
    'HIV/AIDS':                                        'hiv',
    'Hair':                                            'hair',
    'Hearing':                                         'hearing',
    'Heart':                                           'heart',
    'Heart failure':                                   'heart_failure',
    'Heart rate':                                      'heart_rate',
    'Height':                                          'height',
    'Hemophilia':                                      'hemophilia',
    'Hepatic':                                         'hepatic',
    'Hepatitis':                                       'hepatitis',
    'Hormonal':                                        'hormonal',
    "Huntington's disease":                            'huntingtons',
    'Imaging':                                         'imaging',
    'Immune-related':                                  'immune',
    'Infection':                                       'infection',
    'Inflammation':                                    'inflammation',
    'Influenza':                                       'flu',
    'Kidney cancer':                                   'kidney_cancer',
    'Leukemia':                                        'leukemia',
    'Lipids':                                          'lipids',
    'Liver cancer':                                    'liver_cancer',
    'Lung cancer':                                     'lung_cancer',
    'Lymphoma':                                        'lyphoma',
    'Male':                                            'male',
    'Manic depression':                                'manic',
    'Melanoma':                                        'melanoma',
    'Menarche':                                        'menarche',
    'Menopause':                                       'menopause',
    'Methylation':                                     'methylation',
    'Mood disorder':                                   'mood_disorder',
    'Mortality':                                       'mortality',
    'Movement-related':                                'movement',
    'Multiple sclerosis (MS)':                         'ms',
    'Muscle-related':                                  'muscle',
    'Musculoskeletal':                                 'msk',
    'Myasthenia gravis':                               'myasthenia',
    'Myocardial infarction (MI)':                      'mi',
    'Narcotics':                                       'narc',
    'Nasal':                                           'nasal',
    'Nasal cancer':                                    'nasal_cancer',
    'Neuro':                                           'neuro',
    'Obsessive-compulsive disorder (OCD)':             'ocd',
    'Oral cancer':                                     'oral_cancer',
    'Oral-related':                                    'oral',
    'Ovarian cancer':                                  'ovarian_cancer',
    'Pain':                                            'pain',
    'Pancreas':                                        'pancreas',
    'Pancreatic cancer':                               'pancreatic_cancer',
    "Parkinson's disease":                             'parkinsons',
    'Physical activity':                               'activity',
    'Plasma':                                          'plasma',
    'Platelet':                                        'platlet',
    'Pregnancy-related':                               'pregnancy',
    'Prostate cancer':                                 'prostate_cancer',
    'Protein expression':                              'protein_expression',
    'Pulmonary':                                       'pulmonary',
    'Quantitative trait(s)':                           'quantitative',
    'Radiation':                                       'radiation',
    'Rectal cancer':                                   'rectal_cancer',
    'Renal':                                           'renal',
    'Renal cancer':                                    'renal_cancer',
    'Reproductive':                                    'reproductive',
    'Rheumatoid arthritis':                            'rheumatoid',
    'Salmonella':                                      'salmonella',
    'Schizophrenia':                                   'schizophrenia',
    'Serum':                                           'serum',
    'Sickle cell anemia':                              'sickle_cell',
    'Skin cancer':                                     'skin_cancer',
    'Skin-related':                                    'skin',
    'Sleep':                                           'sleep',
    'Smallpox':                                        'smallpox',
    'Smoking':                                         'smoking',
    'Social':                                          'social',
    'Stone':                                           'stone',
    'Stroke':                                          'stroke',
    'Subclinical CVD':                                 'subclin_cvd',
    'Surgery':                                         'surgery',
    'Systemic lupus erythematosus (SLE)':              'sle',
    'T2D-related':                                     't2d_related',
    'Testicular cancer':                               'testicular',
    'Thrombosis':                                      'thrombosis',
    'Thyroid':                                         'thyroid',
    'Thyroid cancer':                                  'thyroid_cancer',
    'Treatment response':                              'treatment_response',
    'Treatment-related':                               'treatment',
    'Tuberculosis':                                    'tb',
    'Type 1 diabetes (T1D)':                           't1d',
    'Type 2 diabetes (T2D)':                           't2d',
    'Ulcerative colitis':                              'ulc_colitis',
    'Upper airway tract cancer':                       'upper_airway_cancer',
    'Urinary':                                         'urinary',
    'Uterine cancer':                                  'uterine_cancer',
    'Uterine fibroids':                                'uterine_fibroids',
    'Vaccine':                                         'vaccine',
    'Valve':                                           'valve',
    'Vasculitis':                                      'vasculitis',
    'Venous':                                          'venous',
    'Weight':                                          'weight',
    'Wound':                                           'wound',
    'miRNA':                                           'mirna',
}

pop_correction = {'European/Unspecified': 'European'}

###############################################################################
#                            RST File Definitions                             #
###############################################################################

PHENO_CATS = """\
The following 179 phenotype categories can be searched by alias or category:

{}
"""

PHENOS = """\
The following phenotypes are stored in the GRASP database (there are 1,209 of
them):

{}
"""

POPS = """\
The following populations are available in the Population table:

{}
"""

FLAGS = """\
The Population table only contains summary level population information, each
study also has counts of discovery and replication populations. To query
studies that only contain certain populations, this module uses bitwise flags.
To make these easier to use, we use the `py-flags
<https://pypi.python.org/pypi/py-flags>`_ package, and map the following
population flags:

{}
"""

TABLE_INFO = """\
Table Columns
=============

The two important tables with the majority of the data are Study and SNP. In
addition, phenotype data is stored in Phenotype and PhenoCats, population data
is in Population, and platforms are in Platform.

.. contents:: **Contents**

Study
-----

To query studies, it is recommended to use the query.get_studies() function.

{study}


SNP
---

{snp}

Phenotype
---------

All available phenotypes are available on the `Phenotypes wiki page
<http://grasp.readthedocs.io/en/latest/query_ref.html#phenotype>`_

- id
- phenotype
- studies (link to Study table)
- snps (link to SNP table)

PhenoCats
---------

All phenotype categories are available on the `Phenotype Categories wiki page
<http://grasp.readthedocs.io/en/latest/query_ref.html#phenocat>`_

- id
- population
- alias
- studies (link to Study table)
- snps (link to SNP table)

Population
----------

- id
- population
- studies (link to Study table)
- snps (link to SNP table)

All population entries are available on the `Populations wiki page
<http://grasp.readthedocs.io/en/latest/query_ref.html#population>`_

Platform
--------

- id
- platform
- studies (link to Study table)
- snps (link to SNP table)
"""
