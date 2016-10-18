"""
Functions for managing the GRASP database.

`get_session()` is used everywhere in the module to create a connection to the
database. `initialize_database()` is used to build the database from the GRASP
file. It takes about an hour 90 minutes to run and will overwrite any existing
database.
"""
import os as _os
from re   import compile  as _recompile
from bz2  import open     as _bopen
from gzip import open     as _zopen
from html import unescape as _unescape

# Date parsing
from datetime import date as _date
from dateutil.parser import parse as _dateparse

# Database
from sqlalchemy     import create_engine as _create_engine
from sqlalchemy.sql import select        as _select
from sqlalchemy.orm import sessionmaker  as _sessionmaker

# Progress bar
from tqdm import tqdm as _tqdm

# Table Declarations
from .tables import Base as _Base
from .tables import Study as _Study
from .tables import SNP as _SNP
from .tables import Phenotype as _Phenotype
from .tables import PhenoCats as _PhenoCats
from .tables import Platform as _Platform
from .tables import Population as _Population
from .tables import snp_pheno_assoc as _snp_pheno_assoc
from .tables import study_pheno_assoc as _study_pheno_assoc
from .tables import study_plat_assoc as _study_plat_assoc

# Database config
from .config import config as _config

# Reference objects
from .ref import PopFlag as _PopFlag
from .ref import pheno_synonyms
from .ref import pop_correction

__all__ = ["get_session", "initialize_database"]

###############################################################################
#                               Core Functions                                #
###############################################################################


def get_session(echo=False):
    """Return a session and engine, uses config file.

    Args:
        echo: Echo all SQL to the console.

    Returns:
        session, engine: A SQLAlchemy session and engine object corresponding
                         to the grasp database for use in querying.
    """
    db_type = _config['DEFAULT']['DatabaseType']
    if db_type == 'sqlite':
        engine_string = ('sqlite:///{db_file}'
                         .format(db_file=_config['sqlite']['DatabaseFile']))
    else:
        engine_string = ('{type}://{user}:{passwd}@{host}/grasp'
                         .format(type=db_type,
                                 user=_config['other']['DatabaseUser'],
                                 passwd=_config['other']['DatabasePass'],
                                 host=_config['other']['DatabaseHost']))
    engine  = _create_engine(engine_string, echo=echo)
    Session = _sessionmaker(bind=engine)
    return Session(), engine


def initialize_database(study_file, grasp_file, commit_every=250000,
                        progress=False):
    """Create the database quickly.

    :study_file:   Tab delimited GRASP study file, available here:
                   `<github.com/MikeDacre/grasp/blob/master/grasp_studies.txt>`_
    :grasp_file:   Tab delimited GRASP file.
    :commit_every: How many rows to go through before commiting to disk.
    :progress:     Display a progress bar (db length hard coded).

    """
    rows        = 0
    count       = commit_every
    pphenos     = {}
    phenos      = {}
    platforms   = {}
    populations = {}


    # Create tables
    _, engine = get_session()
    print('Dropping and creating database tables, this may take a while if',
          'the old database is large.')
    if _config['DEFAULT']['DatabaseType'] == 'sqlite':
        cfile = _os.path.isfile(_config['sqlite']['DatabaseFile'])
        if _os.path.isfile(cfile):
            _os.remove(cfile)
    _Base.metadata.drop_all(engine)
    _Base.metadata.create_all(engine)
    print('Tables created.')
    conn = engine.connect()

    # Get tables
    study_table = _Study.__table__
    snp_table   = _SNP.__table__
    pheno_table = _Phenotype.__table__
    pcat_table  = _PhenoCats.__table__
    plat_table  = _Platform.__table__
    pop_table   = _Population.__table__

    # Create insert statements
    study_ins   = study_table.insert()
    snp_ins     = snp_table.insert()
    pheno_ins   = pheno_table.insert()
    pcat_ins    = pcat_table.insert()
    plat_ins    = plat_table.insert()
    pop_ins     = pop_table.insert()
    phsnp_ins   = _snp_pheno_assoc.insert()
    phstudy_ins = _study_pheno_assoc.insert()
    plstudy_ins = _study_plat_assoc.insert()

    # Unique ID counters
    spare_id = 1
    pheno_id = 1
    pcat_id  = 1
    plat_id  = 1
    pop_id   = 1

    # Lists to hold records
    pheno_records   = []
    pcat_records    = []
    plat_records    = []
    pop_records     = []
    study_records   = []
    snp_records     = []
    phsnp_records   = []
    phstudy_records = []
    plstudy_records = []

    # Platform parsing regex
    plat_parser  = _recompile(r'^([^[]*)\[([^]]+)\]?(.*)')

    # Build study information from study file
    print('Parsing study information.')
    with _open_zipped(study_file) as fin:
        # Drop header
        fin.readline()

        if progress:
            pbar = _tqdm(total=2083, unit='studies')
        for line in fin:
            f = line.rstrip().split('\t')

            # Get primary phenotype
            ppheno = _cleanstr(f[7].strip())
            if ppheno not in pphenos:
                pheno_records.append({'phenotype': ppheno,
                                      'id': pheno_id})
                pphenos[ppheno] = pheno_id
                pheno_id += 1

            # Get phenotype categories
            pheno_cats = f[8].strip().split(';')
            our_phenos = []
            for pcat in pheno_cats:
                pcat = pcat.strip()
                if not pcat:
                    continue
                if pcat not in phenos:
                    pcat_records.append({
                        'id':       pcat_id,
                        'category': pcat,
                        'alias':    pheno_synonyms[pcat],
                    })
                    phenos[pcat] = pcat_id
                    pcat_id += 1
                our_phenos.append(phenos[pcat])

            # Get platform info
            our_platforms = []
            try:
                plat, snp_count, impt = [
                    i.strip() for i in plat_parser.findall(f[18].strip())[0]
                ]
                imputed = True if impt == '(imputed)' else False
                plats = _split_mesy_list(plat)
                for plat in plats:
                    plat = plat.strip()
                    if plat not in platforms:
                        plat_records.append({'id':       plat_id,
                                             'platform': plat})
                        platforms[plat] = plat_id
                        plat_id += 1
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
                    pop_records.append({'id':         pop_id,
                                        'population': pop})
                    populations[pop] = pop_id
                    pop_id += 1
                population = populations[pop]
            except IndexError:
                population = None

            # Set populaion flags
            pflag = _PopFlag
            disc_pop = pflag(0)
            rep_pop  = pflag(0)
            l = len(f)
            if l > 22 and f[22]:
                disc_pop |= pflag.eur
            if l > 23 and f[23]:
                disc_pop |= pflag.afr
            if l > 24 and f[24]:
                disc_pop |= pflag.east_asian
            if l > 25 and f[25]:
                disc_pop |= pflag.south_asian
            if l > 26 and f[26]:
                disc_pop |= pflag.his
            if l > 27 and f[27]:
                disc_pop |= pflag.native
            if l > 28 and f[28]:
                disc_pop |= pflag.micro
            if l > 29 and f[29]:
                disc_pop |= pflag.arab
            if l > 30 and f[30]:
                disc_pop |= pflag.mix
            if l > 31 and f[31]:
                disc_pop |= pflag.uns
            if l > 32 and f[32]:
                disc_pop |= pflag.filipino
            if l > 33 and f[33]:
                disc_pop |= pflag.indonesian
            if l > 35 and f[35]:
                rep_pop |= pflag.eur
            if l > 36 and f[36]:
                rep_pop |= pflag.afr
            if l > 37 and f[37]:
                rep_pop |= pflag.east_asian
            if l > 38 and f[38]:
                rep_pop |= pflag.south_asian
            if l > 39 and f[39]:
                rep_pop |= pflag.his
            if l > 40 and f[40]:
                rep_pop |= pflag.native
            if l > 41 and f[41]:
                rep_pop |= pflag.micro
            if l > 42 and f[42]:
                rep_pop |= pflag.arab
            if l > 43 and f[43]:
                rep_pop |= pflag.mix
            if l > 44 and f[44]:
                rep_pop |= pflag.uns
            if l > 45 and f[45]:
                rep_pop |= pflag.filipino
            if l > 46 and f[46]:
                rep_pop |= pflag.indonesian

            # Set the global population flag
            pop_flag = disc_pop | rep_pop

            # Create study
            study_records.append({
                'id':               int(f[0]),
                'author':           _cleanstr(f[1]),
                'pmid':             _cleanstr(f[2]),
                'grasp_ver':        1 if '1.0' in f[3] else 2,
                'noresults':        True if f[4] else False,
                'results':          int(f[5]),
                'qtl':              True if f[6] == '1' else False,
                'phenotype_id':     pphenos[ppheno],
                'phenotype_desc':   ppheno,
                'phenotype':        pphenos[ppheno],
                'phenotype_cats':   our_phenos,
                'datepub':          _get_date(f[9]),
                'in_nhgri':         _get_bool(f[10]),
                'journal':          _cleanstr(f[11]),
                'title':            _cleanstr(f[12]),
                'locations':        _cleanstr(f[13]),
                'mf':               _get_bool(f[14]),
                'mf_only':          _get_bool(f[15]),
                'sample_size':      _cleanstr(f[16]),
                'replication_size': _cleanstr(f[17]),
                'platforms':        platforms,
                'snp_count':        snp_count,
                'imputed':          imputed,
                'population_id':    population,
                'population':       population,
                'total':            int(f[20]),
                'total_disc':       int(f[21]),
                'pop_flag':         int(pop_flag),
                'disc_pop_flag':    int(disc_pop),
                'european':         int(f[22]) if l > 22 and f[22] else None,
                'african':          int(f[23]) if l > 23 and f[23] else None,
                'east_asian':       int(f[24]) if l > 24 and f[24] else None,
                'south_asian':      int(f[25]) if l > 25 and f[25] else None,
                'hispanic':         int(f[26]) if l > 26 and f[26] else None,
                'native':           int(f[27]) if l > 27 and f[27] else None,
                'micronesian':      int(f[28]) if l > 28 and f[28] else None,
                'arab':             int(f[29]) if l > 29 and f[29] else None,
                'mixed':            int(f[30]) if l > 30 and f[30] else None,
                'unspecified':      int(f[31]) if l > 31 and f[31] else None,
                'filipino':         int(f[32]) if l > 32 and f[32] else None,
                'indonesian':       int(f[33]) if l > 33 and f[33] else None,
                'total_rep':        int(f[34]) if l > 34 and f[34] else None,
                'rep_pop_flag':     int(rep_pop),
                'rep_european':     int(f[35]) if l > 35 and f[35] else None,
                'rep_african':      int(f[36]) if l > 36 and f[36] else None,
                'rep_east_asian':   int(f[37]) if l > 37 and f[37] else None,
                'rep_south_asian':  int(f[38]) if l > 38 and f[38] else None,
                'rep_hispanic':     int(f[39]) if l > 39 and f[39] else None,
                'rep_native':       int(f[40]) if l > 40 and f[40] else None,
                'rep_micronesian':  int(f[41]) if l > 41 and f[41] else None,
                'rep_arab':         int(f[42]) if l > 42 and f[42] else None,
                'rep_mixed':        int(f[43]) if l > 43 and f[43] else None,
                'rep_unspecified':  int(f[44]) if l > 44 and f[44] else None,
                'rep_filipino':     int(f[45]) if l > 45 and f[45] else None,
                'rep_indonesian':   int(f[46]) if l > 46 and f[46] else None,
            })

            # Create association records
            for i in our_phenos:
                phstudy_records.append({'study_id':    int(f[0]),
                                        'pheno_id':    i})
            for i in our_platforms:
                plstudy_records.append({'study_id':    int(f[0]),
                                        'platform_id': i})

            pbar.update()

    pbar.close()
    print('Writing study information...')
    conn.execute(pheno_ins, pheno_records)
    conn.execute(pcat_ins, pcat_records)
    conn.execute(plat_ins, plat_records)
    conn.execute(pop_ins, pop_records)
    conn.execute(study_ins, study_records)
    conn.execute(phstudy_ins, phstudy_records)
    conn.execute(plstudy_ins, plstudy_records)
    print('Done')

    # Reinitialize lists for main GRASP parser
    pheno_records   = []
    pcat_records    = []
    plat_records    = []
    pop_records     = []

    # Get full study info from database for use in SNPs
    sinfo = conn.execute(_select([study_table.c.id, study_table.c.pmid])).fetchall()
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

    print('Parsing SNP information...')
    with _open_zipped(grasp_file, encoding='latin1') as fin:
        # Drop header
        fin.readline()

        if progress:
            pbar = _tqdm(total=8864717, unit='snps')

        for line in fin:
            f = line.rstrip().split('\t')

            # Get primary phenotype
            ppheno = _cleanstr(f[11])
            # These are poorly curated, so there is no need to use a
            # separate table for them.
            #  if ppheno not in pphenos:
                #  conn.execute(pheno_ins.values(
                    #  phenotype=ppheno
                #  ))
                #  pphenos[ppheno] = conn.execute(
                    #  select([pheno_table.c.id]).where(
                        #  pheno_table.c.phenotype == ppheno
                    #  )
                #  ).first()[0]

            # Get phenotype categories
            pheno_cats = f[13].strip().split(';')
            our_phenos = []
            for pcat in pheno_cats:
                pcat = pcat.strip()
                if not pcat:
                    continue
                if pcat not in phenos:
                    pcat_records.append({
                        'id':       pcat_id,
                        'category': pcat,
                        'alias':    pheno_synonyms[pcat],
                    })
                    phenos[pcat] = pcat_id
                    pcat_id += 1
                our_phenos.append(phenos[pcat])

            # Get population description
            try:
                pop = f[23].strip()
                try:
                    pop = pop_correction[pop]
                except KeyError:
                    pass
                if pop not in populations:
                    pop_records.append({'id':         pop_id,
                                        'population': pop})
                    populations[pop] = pop_id
                    pop_id += 1
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
                'phenotype_desc':   ppheno,
                'phenotype_cats':   our_phenos,
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
                    pbar.write('Writing rows...')
                else:
                    print('Writing rows...')
                if pcat_records:
                    conn.execute(pcat_ins, pcat_records)
                if plat_records:
                    conn.execute(plat_ins, plat_records)
                if pop_records:
                    conn.execute(pop_ins, pop_records)
                conn.execute(snp_ins, snp_records)
                conn.execute(phsnp_ins, phsnp_records)
                if progress:
                    pbar.write('{} rows written'.format(rows))
                else:
                    print('{} rows written'.format(rows))
                count         = commit_every-1
                pcat_records  = []
                plat_records  = []
                pop_records   = []
                snp_records   = []
                phsnp_records = []
            rows += 1
            if progress:
                pbar.update()

        # Final insert
        pbar.close()
        print('Writing final rows...')
        conn.execute(snp_ins, snp_records)
        conn.execute(phsnp_ins, phsnp_records)
        print('{} rows written'.format(rows))
        print('Done!')


###############################################################################
#                              Support Functions                              #
###############################################################################


_rmspace  = _recompile(r'  +')
def _cleanstr(string):
    """Run a few regex cleanups on a string.

    Strips unneeded starting characters, trims extra spaces, and converts
    mangeled unicode characters from Excel into readable characters.
    """
    cstr = _rmspace.sub(' ', string.strip(" \"'"))
    return _unescape(cstr)


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
        return _date.fromordinal(_dateparse(string).toordinal())
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
            return _zopen(infile, mode)
        if infile.endswith('.bz2'):
            return _bopen(infile, mode)
        return open(infile, p2mode, encoding=encoding)
