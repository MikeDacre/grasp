"""
Functions for managing the GRASP database.

       Created: 2016-10-08
 Last modified: 2016-10-12 20:58

"""
import re
import sys
import bz2
import gzip

# Date parsing
from datetime import date
from dateutil.parser import parse as dateparse

# Database
from sqlalchemy import create_engine
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker

# Bitwise flags
from flags import Flags

# Progress bar
from tqdm import tqdm

# Table Declarations
from .tables import Base, Study, SNP, Phenotype, Platform, Population
from .tables import snp_pheno_assoc, study_pheno_assoc, study_plat_assoc

# Database config
from .config import config


###############################################################################
#                          Population Bitwise Flags                           #
###############################################################################


class PopFlag(Flags):

    """A simplified bitwise flag system for tracking populations."""

    eur         = ()  #  European
    afr         = ()  #  African ancestry
    east_asian  = ()  #  East Asian
    south_asian = ()  #  Indian/South Asian
    his         = ()  #  Hispanic
    native      = ()  #  Native
    micro       = ()  #  Micronesian
    arab        = ()  #  Arab/ME
    mix         = ()  #  Mixed
    uns         = ()  #  Unspec
    filipino    = ()  #  Filipino
    indonesian  = ()  #  Indonesian


###############################################################################
#                             Population Synonyms                             #
###############################################################################


pop_synonyms = {
    'Allergy':                                         allergy,
    'Addiction':                                       addiction,
    'Adipose-related':                                 adipose,
    'Adverse drug reaction (ADR)':                     adr,
    'Age-related macular degeneration (ARMD)':         armd,
    'Aging':                                           aging,
    'Alcohol':                                         alcohol,
    "Alzheimer's disease":                             alzheimers,
    'Amyotrophic lateral sclerosis (ALS)':             als,
    'Anemia':                                          anemia,
    'Aneurysm':                                        aneurysm,
    'Anthrax':                                         anthrax,
    'Anthropometric':                                  anthropometric,
    'Arterial':                                        arterial,
    'Arthritis':                                       arthritis,
    'Asthma':                                          asthma,
    'Atrial fibrillation':                             afib,
    'Attention-deficit/hyperactivity disorder (ADHD)': adhd,
    'Autism':                                          autism,
    'Basal cell cancer':                               basal_cell_cancer,
    'Behavioral':                                      behavioral,
    'Bipolar disorder':                                bipolar,
    'Bladder cancer':                                  bladder_cancer,
    'Bleeding disorder':                               bleeding_disorder,
    'Blood':                                           blood,
    'Blood cancer':                                    blood_cancer,
    'Blood pressure':                                  bp,
    'Blood-related':                                   blood,
    'Body mass index':                                 bmi,
    'Bone cancer':                                     bone_cancer,
    'Bone-related':                                    bone,
    'Brain cancer':                                    brain_cancer,
    'Breast cancer':                                   breast_cancer,
    'C-reactive protein (CRP)':                        crp,
    'CVD':                                             cvd,
    'CVD risk factor (CVD RF)':                        cvd_rf,
    'Calcium':                                         calcium,
    'Cancer':                                          cancer,
    'Cancer-related':                                  cancer_related,
    'Cardiomyopathy':                                  152,
    'Cardiovascular disease (CVD)':                    38,
    'Celiac disease':                                  162,
    'Cell line':                                       9,
    'Cervical cancer':                                 158,
    'Chronic kidney disease':                          113,
    'Chronic lung disease':                            3,
    'Chronic obstructive pulmonary disease (COPD)':    140,
    'Cognition':                                       107,
    'Colorectal cancer':                               66,
    'Congenital':                                      96,
    'Coronary heart disease (CHD)':                    120,
    "Crohn's disease":                                 63,
    'Cystic fibrosis':                                 110,
    'Cytotoxicity':                                    169,
    'Dental':                                          48,
    'Depression':                                      104,
    'Developmental':                                   43,
    'Diet-related':                                    100,
    'Drug response':                                   26,
    'Drug treatment':                                  179,
    'Emphysema':                                       168,
    'Endometrial cancer':                              11,
    'Environment':                                     87,
    'Epigenetics':                                     22,
    'Epilepsy':                                        83,
    'Esophageal cancer':                               70,
    'Eye-related':                                     17,
    'Female':                                          14,
    'Gallbladder cancer':                              67,
    'Gallstones':                                      125,
    'Gastric cancer':                                  147,
    'Gastrointestinal':                                65,
    'Gender':                                          13,
    'Gene expression (RNA)':                           19,
    'Gene expression (protein)':                       6,
    'General health':                                  167,
    'Glaucoma':                                        97,
    'Graft-versus-host':                               164,
    "Grave's disease":                                 94,
    'HIV/AIDS':                                        35,
    'Hair':                                            124,
    'Hearing':                                         148,
    'Heart':                                           37,
    'Heart failure':                                   163,
    'Heart rate':                                      149,
    'Height':                                          128,
    'Hemophilia':                                      154,
    'Hepatic':                                         89,
    'Hepatitis':                                       118,
    'Hormonal':                                        42,
    "Huntington's disease":                            88,
    'Imaging':                                         73,
    'Immune-related':                                  50,
    'Infection':                                       33,
    'Inflammation':                                    4,
    'Influenza':                                       117,
    'Kidney cancer':                                   150,
    'Leukemia':                                        53,
    'Lipids':                                          28,
    'Liver cancer':                                    136,
    'Lung cancer':                                     58,
    'Lymphoma':                                        54,
    'Male':                                            78,
    'Manic depression':                                175,
    'Melanoma':                                        157,
    'Menarche':                                        134,
    'Menopause':                                       45,
    'Methylation':                                     21,
    'Mood disorder':                                   166,
    'Mortality':                                       31,
    'Movement-related':                                130,
    'Multiple sclerosis (MS)':                         109,
    'Muscle-related':                                  93,
    'Musculoskeletal':                                 114,
    'Myasthenia gravis':                               146,
    'Myocardial infarction (MI)':                      39,
    'Narcotics':                                       139,
    'Nasal':                                           71,
    'Nasal cancer':                                    151,
    'Neuro':                                           20,
    'Obsessive-compulsive disorder (OCD)':             142,
    'Oral cancer':                                     119,
    'Oral-related':                                    46,
    'Ovarian cancer':                                  135,
    'Pain':                                            143,
    'Pancreas':                                        57,
    'Pancreatic cancer':                               56,
    "Parkinson's disease":                             101,
    'Physical activity':                               16,
    'Plasma':                                          76,
    'Platelet':                                        98,
    'Pregnancy-related':                               32,
    'Prostate cancer':                                 79,
    'Protein expression':                              7,
    'Pulmonary':                                       2,
    'Quantitative trait(s)':                           5,
    'Radiation':                                       144,
    'Rectal cancer':                                   159,
    'Renal':                                           91,
    'Renal cancer':                                    122,
    'Reproductive':                                    12,
    'Rheumatoid arthritis':                            62,
    'Salmonella':                                      141,
    'Schizophrenia':                                   80,
    'Serum':                                           30,
    'Sickle cell anemia':                              126,
    'Skin cancer':                                     156,
    'Skin-related':                                    69,
    'Sleep':                                           68,
    'Smallpox':                                        121,
    'Smoking':                                         82,
    'Social':                                          90,
    'Stone':                                           92,
    'Stroke':                                          51,
    'Subclinical CVD':                                 77,
    'Surgery':                                         36,
    'Systemic lupus erythematosus (SLE)':              55,
    'T2D-related':                                     170,
    'Testicular cancer':                               161,
    'Thrombosis':                                      103,
    'Thyroid':                                         41,
    'Thyroid cancer':                                  40,
    'Treatment response':                              15,
    'Treatment-related':                               171,
    'Tuberculosis':                                    34,
    'Type 1 diabetes (T1D)':                           60,
    'Type 2 diabetes (T2D)':                           18,
    'Ulcerative colitis':                              138,
    'Upper airway tract cancer':                       172,
    'Urinary':                                         85,
    'Uterine cancer':                                  173,
    'Uterine fibroids':                                174,
    'Vaccine':                                         116,
    'Valve':                                           132,
    'Vasculitis':                                      137,
    'Venous':                                          102,
    'Weight':                                          74,
    'Wound':                                           64,
    'miRNA':                                           129
}



###############################################################################
#                               Core Functions                                #
###############################################################################


def get_session(echo=False):
    """Return a session and engine, uses config file."""
    db_type = config['DEFAULT']['DatabaseType']
    if db_type == 'sqlite':
        engine_string = ('sqlite:///{db_file}'
                         .format(db_file=config['sqlite']['DatabaseFile']))
    else:
        engine_string = ('{type}://{user}:{passwd}@{host}/grasp'
                         .format(type=db_type,
                                 user=config['other']['DatabaseUser'],
                                 passwd=config['other']['DatabasePass'],
                                 host=config['other']['DatabaseHost']))
    engine  = create_engine(engine_string, echo=echo)
    Session = sessionmaker(bind=engine)
    return Session(), engine


def initialize_database(study_file, grasp_file, commit_every=250000,
                        progress=True):
    """Create the database quickly.

    :study_file:   Tab delimited GRASP study file, available here:
                   github.com/MikeDacre/grasp/blob/master/grasp_studies.txt
    :grasp_file:   Tab delimited GRASP file.
    :commit_every: How many rows to go through before commiting to disk.
    :progress:     Display a progress bar (db length hard coded).

    """
    rows        = 0
    count       = commit_every
    phenos      = {}
    platforms   = {}
    populations = {}

    # Correction tables
    pop_correction = {'European/Unspecified': 'European'}

    # Create tables
    _, engine = get_session()
    print('Dropping and creating database tables, this may take a while if',
          'the old database is large. If using sqlite, you can just delete',
          'the file to speed up this step.')
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print('Tables created.')
    conn = engine.connect()

    # Get tables
    study_table = Study.__table__
    snp_table   = SNP.__table__
    pheno_table = Phenotype.__table__
    plat_table  = Platform.__table__
    pop_table   = Population.__table__

    # Create insert statements
    study_ins   = study_table.insert()
    snp_ins     = snp_table.insert()
    pheno_ins   = pheno_table.insert()
    plat_ins    = plat_table.insert()
    pop_ins     = pop_table.insert()
    phsnp_ins   = snp_pheno_assoc.insert()
    phstudy_ins = study_pheno_assoc.insert()
    plstudy_ins = study_plat_assoc.insert()

    spare_id        = 1
    study_records   = []
    snp_records     = []
    phsnp_records   = []
    phstudy_records = []
    plstudy_records = []

    # Build study information from study file
    sys.stdout.write('Parsing study information.\n')
    with _open_zipped(study_file) as fin:
        # Drop header
        fin.readline()

        for line in fin:
            f = line.rstrip().split('\t')

            # Get phenotype categories
            pheno_cats = f[8].strip().split(';')
            our_phenos = []
            for pcat in pheno_cats:
                pcat.strip()
                if not pcat:
                    continue
                if pcat not in phenos:
                    conn.execute(pheno_ins.values(category=pcat))
                    phenos[pcat] = conn.execute(
                        select([pheno_table.c.id]).where(
                            pheno_table.c.category == pcat
                        )
                    ).first()[0]
                our_phenos.append(phenos[pcat])

            # Get platform info
            our_platforms = []
            try:
                plat, snp_count, impt = [
                    i.strip() for i in re.findall(r'^([^[]*)\[([^]]+)\]?(.*)',
                                                  f[18].strip())[0]
                ]
                imputed = True if impt == '(imputed)' else False
                plats = _split_mesy_list(plat)
                for plat in plats:
                    plat = plat.strip()
                    if plat not in platforms:
                        conn.execute(plat_ins.values(platform=plat))
                        platforms[plat] = conn.execute(
                            select([plat_table.c.id]).where(
                                plat_table.c.platform == plat
                            )
                        ).first()[0]
                    our_platforms.append(platforms[plat])
            except IndexError:
                plat, snp_count, impt = None, None, None
                imputed = None

            # Get population description
            try:
                pop = f[19].strip()
                try:
                    pop = pop_correction[pop]
                except KeyError:
                    pass
                if pop not in populations:
                    conn.execute(pop_ins.values(population=pop))
                    populations[pop] = conn.execute(
                        select([pop_table.c.id]).where(
                            pop_table.c.population == pop
                        )
                    ).first()[0]
                population = populations[pop]
            except IndexError:
                population = None

            # Set populaion flags
            p = PopFlag
            disc_pop = p(0)
            rep_pop  = p(0)
            l = len(f)
            if l > 22 and f[22]:
                disc_pop |= p.eur
            if l > 23 and f[23]:
                disc_pop |= p.afr
            if l > 24 and f[24]:
                disc_pop |= p.east_asian
            if l > 25 and f[25]:
                disc_pop |= p.south_asian
            if l > 26 and f[26]:
                disc_pop |= p.his
            if l > 27 and f[27]:
                disc_pop |= p.native
            if l > 28 and f[28]:
                disc_pop |= p.micro
            if l > 29 and f[29]:
                disc_pop |= p.arab
            if l > 30 and f[30]:
                disc_pop |= p.mix
            if l > 31 and f[31]:
                disc_pop |= p.uns
            if l > 32 and f[32]:
                disc_pop |= p.filipino
            if l > 33 and f[33]:
                disc_pop |= p.indonesian
            if l > 35 and f[35]:
                rep_pop |= p.eur
            if l > 36 and f[36]:
                rep_pop |= p.afr
            if l > 37 and f[37]:
                rep_pop |= p.east_asian
            if l > 38 and f[38]:
                rep_pop |= p.south_asian
            if l > 39 and f[39]:
                rep_pop |= p.his
            if l > 40 and f[40]:
                rep_pop |= p.native
            if l > 41 and f[41]:
                rep_pop |= p.micro
            if l > 42 and f[42]:
                rep_pop |= p.arab
            if l > 43 and f[43]:
                rep_pop |= p.mix
            if l > 44 and f[44]:
                rep_pop |= p.uns
            if l > 45 and f[45]:
                rep_pop |= p.filipino
            if l > 46 and f[46]:
                rep_pop |= p.indonesian

            # Create study
            study_records.append({
                'id':               int(f[0]),
                'author':           f[1].strip(),
                'pmid':             f[2].strip(),
                'grasp_ver':        1 if '1.0' in f[3] else 2,
                'noresults':        True if f[4] else False,
                'results':          int(f[5]),
                'qtl':              True if f[6] == '1' else False,
                'pheno_desc':       f[7].strip(),
                'phenotypes':       our_phenos,
                'datepub':          _get_date(f[9]),
                'in_nhgri':         _get_bool(f[10]),
                'journal':          f[11].strip(),
                'title':            f[12].strip(),
                'locations':        f[13].strip(),
                'mf':               _get_bool(f[14]),
                'mf_only':          _get_bool(f[15]),
                'sample_size':      f[16].strip(),
                'replication_size': f[17].strip(),
                'platforms':        platforms,
                'snp_count':        snp_count,
                'imputed':          imputed,
                'population_id':    population,
                'population':       population,
                'total':            int(f[20]),
                'total_disc':       int(f[21]),
                'disc_pop':         disc_pop,
                'european':         int(f[22]) if l > 22 and f[22] else None,
                'african':          int(f[23]) if l > 23 and f[23] else None,
                'east_asian':       int(f[24]) if l > 24 and f[24] else None,
                'south_asian':      int(f[25]) if l > 25 and f[25] else None,
                'hispanic':         int(f[26]) if l > 26 and f[26] else None,
                'native':           int(f[27]) if l > 27 and f[27] else None,
                'micronesian':      int(f[28]) if l > 28 and f[28] else None,
                'arab':             int(f[29]) if l > 29 and f[29] else None,
                'mixed':            int(f[30]) if l > 30 and f[30] else None,
                'unpecified':       int(f[31]) if l > 31 and f[31] else None,
                'filipino':         int(f[32]) if l > 32 and f[32] else None,
                'indonesian':       int(f[33]) if l > 33 and f[33] else None,
                'total_rep':        int(f[34]) if l > 34 and f[34] else None,
                'rep_pop':          rep_pop,
                'rep_european':     int(f[35]) if l > 35 and f[35] else None,
                'rep_african':      int(f[36]) if l > 36 and f[36] else None,
                'rep_east_asian':   int(f[37]) if l > 37 and f[37] else None,
                'rep_south_asian':  int(f[38]) if l > 38 and f[38] else None,
                'rep_hispanic':     int(f[39]) if l > 39 and f[39] else None,
                'rep_native':       int(f[40]) if l > 40 and f[40] else None,
                'rep_micronesian':  int(f[41]) if l > 41 and f[41] else None,
                'rep_arab':         int(f[42]) if l > 42 and f[42] else None,
                'rep_mixed':        int(f[43]) if l > 43 and f[43] else None,
                'rep_unpecified':   int(f[44]) if l > 44 and f[44] else None,
                'rep_filipino':     int(f[45]) if l > 45 and f[45] else None,
                'rep_indonesian':   int(f[46]) if l > 46 and f[46] else None,
            })

            # Create association records
            for i in our_phenos:
                phstudy_records.append({'study_id' : int(f[0]), 'pheno_id' : i})
            for i in our_platforms:
                plstudy_records.append({'study_id' : int(f[0]), 'platform_id' : i})

    sys.stdout.write('Writing study information...\n')
    conn.execute(study_ins, study_records)
    conn.execute(phstudy_ins, phstudy_records)
    conn.execute(plstudy_ins, plstudy_records)

    sinfo = conn.execute(select([study_table.c.id, study_table.c.pmid])).fetchall()
    studies = {}
    for i, p in sinfo:
        studies[p] = i
    no_pmid = {
        'Dissertation (https://openaccess.leidenuniv.nl/handle/1887/17746)':                                                                          1,
        'KARE Genomewide Association Study of Blood Pressure Using Imputed SNPs':                                                                     2,
        'Genome-wide Association Study Identification of a New Genetic Locus with Susceptibility to Osteoporotic Fracture in the Korean Population.': 3,
        'Genome-wide Association Study Identified TIMP2 Genetic Variant with Susceptibility to Osteoarthritis':                                       4,
        'Application of Structural Equation Models to Genome-wide Association Analysis ':                                                             5,
        'Comparison of Erythrocyte Traits Among European, Japanese and Korean':                                                                       6,
        'Genomewide Association Study Identification of a New Genetic Locus with Susceptibility to Osteoporotic Fracture in the Korean Population':   7,
        'Joint identification of multiple genetic variants of obesity in A Korean Genome-wide association study':                                     8,
        'Genome-Wide Association Analyses on Blood Pressure Using Three Different Phenotype Definitions':                                             9,
        'Association of intronic sequence variant in the gene encoding spleen tyrosine kinase with susceptibility to vascular dementia':              10,
    }

    sys.stdout.write('Parsing SNP information\n')
    with _open_zipped(grasp_file, encoding='latin1') as fin:
        # Drop header
        fin.readline()

        if progress:
            pbar = tqdm(total=8864718, unit='snps')

        for line in fin:
            f = line.rstrip().split('\t')

            # Get phenotype categories
            pheno_cats = f[13].strip().split(';')
            our_phenos = []
            for pcat in pheno_cats:
                if pcat not in phenos:
                    conn.execute(pheno_ins.values(category=pcat))
                    phenos[pcat] = conn.execute(
                        select([pheno_table.c.id]).where(
                            pheno_table.c.category == pcat
                        )
                    ).first()[0]
                our_phenos.append(phenos[pcat])

            # Get population description
            try:
                pop = f[23].strip()
                if pop in pop_correction:
                    pop = pop_correction[pop]
                if pop not in populations:
                    conn.execute(pop_ins.values(population=pop))
                    populations[pop] = conn.execute(
                        select([pop_table.c.id]).where(
                            pop_table.c.population == pop
                        )
                    ).first()[0]
                population = populations[pop]
            except IndexError:
                population = None

            # Create record for SNP
            try:
                sid       = int(f[0])
            except ValueError:
                sid       = spare_id
                spare_id += 1
            l = len(f)
            try:
                study = studies[f[7].strip()]
            except KeyError:
                study = no_pmid[f[17].strip()]
            record = {
                'id':               sid,
                'NHLBIkey':         f[0],
                'HUPfield':         f[1],
                'LastCurationDate': _get_date(f[2]),
                'CreationDate':     _get_date(f[3]),
                'snpid':            f[4],
                'chrom':            f[5],
                'pos':              int(f[6]),
                'population_id':    population,
                'population':       population,
                'study_id':         study,
                'study':            study,
                'study_snpid':      f[8],
                'paper_loc':        f[9],
                'pval':             float(f[10]) if f[10] else None,
                'primary_pheno':    f[11] if l > 12 else None,
                'phenotypes':       our_phenos,
            }
            record['InGene']             = f[51] if l > 52 else None
            record['NearestGene']        = f[52] if l > 53 else None
            record['InLincRNA']          = f[53] if l > 54 else None
            record['InMiRNA']            = f[54] if l > 55 else None
            record['InMiRNABS']          = f[55] if l > 56 else None
            record['dbSNPfxn']           = f[56] if l > 57 else None
            record['dbSNPMAF']           = f[57] if l > 58 else None
            record['dbSNPinfo']          = f[58] if l > 59 else None
            record['dbSNPvalidation']    = f[59] if l > 60 else None
            record['dbSNPClinStatus']    = f[60] if l > 61 else None
            record['ORegAnno']           = f[61] if l > 62 else None
            record['ConservPredTFBS']    = f[62] if l > 63 else None
            record['HumanEnhancer']      = f[63] if l > 64 else None
            record['RNAedit']            = f[64] if l > 65 else None
            record['PolyPhen2']          = f[65] if l > 66 else None
            record['SIFT']               = f[66] if l > 67 else None
            record['LSSNP']              = f[67] if l > 68 else None
            record['UniProt']            = f[68] if l > 69 else None
            record['EqtlMethMetabStudy'] = f[69] if l > 70 else None
            snp_records.append(record)

            # Create association records
            for i in our_phenos:
                phsnp_records.append({'snp_id' : sid, 'pheno_id' : i})

            # Decide when to execute
            if count:
                count -= 1
            else:
                if progress:
                    tqdm.write('Writing rows...')
                else:
                    sys.stdout.write('Writing rows...\n')
                conn.execute(snp_ins, snp_records)
                conn.execute(phsnp_ins, phsnp_records)
                if progress:
                    tqdm.write('{} rows written'.format(rows))
                else:
                    sys.stdout.write('{} rows written\n'.format(rows))
                count           = 49999
                snp_records     = []
                phsnp_records = []
            rows += 1
            if progress:
                pbar.update()

        # Final insert
        sys.stdout.write('Writing final rows...\n')
        conn.execute(snp_ins, snp_records)
        conn.execute(phsnp_ins, phsnp_records)
        sys.stdout.write('{} rows written\n'.format(rows))
        sys.stdout.write('Done!\n')


###############################################################################
#                              Support Functions                              #
###############################################################################


def _split_mesy_list(string):
    """Split a string that contains commas and 'ands/&'

    :string:  A string with commas/ands/&
    :returns: A list

    """
    init_list  = [i.strip() for i in string.split(',') if i]
    final_list = []
    for i in init_list:
        if i.isspace():
            continue
        andlist = i.split('and')
        amplist = i.split('&')
        if len(andlist) > 1:
            for j in andlist:
                if not j or j.isspace():
                    continue
                final_list.append(j.strip())
        elif len(amplist) > 1:
            for j in amplist:
                if not j or j.isspace():
                    continue
                final_list.append(j.strip())
        else:
            final_list.append(i.strip())
    final_list = [i.strip() for i in final_list if not i.isspace()]
    return [i for i in final_list if i]


def _get_date(string):
    """Return datetime date object from string."""
    try:
        return date.fromordinal(dateparse(string).toordinal())
    except ValueError:
        print(string)
        raise


def _get_bool(string):
    """Return a bool from a string of y/n."""
    string = string.lower()
    return True if string == 'y' else False


def _open_zipped(infile, mode='r', encoding='utf-8'):
    """ Return file handle of file regardless of zipped or not
        Text mode enforced for compatibility with python2 """
    mode   = mode[0] + 't'
    p2mode = mode
    if hasattr(infile, 'write'):
        return infile
    if isinstance(infile, str):
        if infile.endswith('.gz'):
            return gzip.open(infile, mode)
        if infile.endswith('.bz2'):
            if hasattr(bz2, 'open'):
                return bz2.open(infile, mode)
            else:
                return bz2.BZ2File(infile, p2mode)
        return open(infile, p2mode, encoding=encoding)
