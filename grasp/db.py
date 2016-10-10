"""
Functions for managing the GRASP database.

       Created: 2016-10-08
 Last modified: 2016-10-10 12:13

"""
import re
import sys
import bz2
import gzip

from datetime import date
from dateutil.parser import parse as dateparse

from sqlalchemy import create_engine
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker

# Progress bar
from tqdm import tqdm

from .tables import Base, SNP, Phenotype, Platform, Population
from .tables import pheno_assoc_table, plat_assoc_table

###############################################################################
#                               Core Functions                                #
###############################################################################


def get_session(db='grasp.db', echo=False):
    """Return a session and engine."""
    engine  = create_engine('sqlite:///{}'.format(db), echo=echo)
    Session = sessionmaker(bind=engine)
    return Session(), engine


def initialize_database(grasp_file, dbfile='grasp.db', commit_every=50000,
                        progress=True):
    """Create the database quickly.

    :grasp_file:   Tab delimited GRASP file.
    :db_file:      The sqlite database file to write to.
    :commit_every: How many rows to go through before commiting to disk.
    :progress:     Display a progress bar (db length hard coded).

    """
    rows        = 0
    count       = commit_every
    phenos      = {}
    platforms   = {}
    populations = {}

    # Create tables
    _, engine = get_session(dbfile)
    Base.metadata.create_all(engine)
    conn = engine.connect()

    # Get tables
    snp_table   = SNP.__table__
    pheno_table = Phenotype.__table__
    plat_table  = Platform.__table__
    pop_table   = Population.__table__

    # Create insert statements
    snp_ins     = snp_table.insert()
    pheno_ins   = pheno_table.insert()
    plat_ins    = plat_table.insert()
    pop_ins     = pop_table.insert()
    phassoc_ins = pheno_assoc_table.insert()
    plassoc_ins = plat_assoc_table.insert()

    spare_id        = 1
    snp_records     = []
    phassoc_records = []
    plassoc_records = []

    with open_zipped(grasp_file, encoding='latin1') as fin:
        # Drop header
        fin.readline()
        if progress:
            pbar = tqdm(total=8864718, unit='rows')
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

            # Get platform info
            our_platforms = []
            try:
                plat, snp_count, impt = [
                    i.strip() for i in re.findall(r'^([^[]*)\[([^]]+)\]?(.*)',
                                                  f[22].strip())[0]
                ]
                imputed = True if impt == '(imputed)' else False
                plats = split_messy_list(plat)
                for plat in plats:
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
                pop = f[23].strip()
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
            record = {
                'id'                          : sid,
                'HUPfield'                    : f[1],
                'LastCurationDate'            : get_date(f[2]),
                'CreationDate'                : get_date(f[3]),
                'SNPid'                       : f[4],
                'chrom'                       : f[5],
                'pos'                         : int(f[6]),
                'PMID'                        : f[7],
                'SNPid_paper'                 : f[8],
                'LocationWithinPaper'         : f[9],
                'Pvalue'                      : float(f[10]) if f[10] else None,
                'Phenotype'                   : f[11] if l > 12 else None,
                'PaperPhenotypeDescription'   : f[12] if l > 13 else None,
                'phenotypes'                  : our_phenos,
                'DatePub'                     : get_date(f[14]) if l > 15 else None,
                'InNHGRIcat'                  : get_bool(f[15]) if l > 16 else None,
                'Journal'                     : f[16] if l > 17 else None,
                'Title'                       : f[17] if l > 18 else None,
                'MF_analysis'                 : get_bool(f[18]) if l > 19 else None,
                'MF_analysis_exclusive'       : get_bool(f[19]) if l > 20 else None,
                'sample_desc'                 : f[20] if l > 21 else None,
                'rep_sample_desc'             : f[21] if l > 22 else None,
                'platforms'                   : platforms,
                'snp_count'                   : snp_count,
                'imputed'                     : imputed,
                'population'                  : population,
                'TotalSamples'                : int(f[24]) if l > 25 and f[24] else None,
                'TotalDiscoverySamples'       : int(f[25]) if l > 26 and f[25] else None,
            }
            record['EuropeanDiscovery'] = int(f[26]) if l > 28 and f[26] else None
            record['AfricanDiscovery']  = int(f[27]) if l > 28 and f[27] else None
            record['EastAsianDiscovery']            = f[28] if l > 29 else None
            record['IndianSouthAsianDiscovery']     = f[29] if l > 30 else None
            record['HispanicDiscovery']             = f[30] if l > 31 else None
            record['NativeDiscovery']               = f[31] if l > 32 else None
            record['MicronesianDiscovery']          = f[32] if l > 33 else None
            record['ArabMEDiscovery']               = f[33] if l > 34 else None
            record['MixedDiscovery']                = f[34] if l > 35 else None
            record['UnspecifiedDiscovery']          = f[35] if l > 36 else None
            record['FilipinoDiscovery']             = f[36] if l > 37 else None
            record['IndonesianDiscovery']           = f[37] if l > 38 else None
            record['Totalreplicationsamples']       = f[38] if l > 39 else None
            record['EuropeanReplication']           = f[39] if l > 40 else None
            record['AfricanReplication']            = f[40] if l > 41 else None
            record['EastAsianReplication']          = f[41] if l > 42 else None
            record['IndianSouthAsianReplication']   = f[42] if l > 43 else None
            record['HispanicReplication']           = f[43] if l > 44 else None
            record['NativeReplication']             = f[44] if l > 45 else None
            record['MicronesianReplication']        = f[45] if l > 46 else None
            record['ArabMEReplication']             = f[46] if l > 47 else None
            record['MixedReplication']              = f[47] if l > 48 else None
            record['UnspecifiedReplication']        = f[48] if l > 49 else None
            record['FilipinoReplication']           = f[49] if l > 50 else None
            record['IndonesianReplication']         = f[50] if l > 51 else None
            record['InGene']                        = f[51] if l > 52 else None
            record['NearestGene']                   = f[52] if l > 53 else None
            record['InLincRNA']                     = f[53] if l > 54 else None
            record['InMiRNA']                       = f[54] if l > 55 else None
            record['InMiRNABS']                     = f[55] if l > 56 else None
            record['dbSNPfxn']                      = f[56] if l > 57 else None
            record['dbSNPMAF']                      = f[57] if l > 58 else None
            record['dbSNPalleles']                  = f[58] if l > 59 else None
            record['dbSNPvalidation']               = f[59] if l > 60 else None
            record['dbSNPClinStatus']               = f[60] if l > 61 else None
            record['ORegAnno']                      = f[61] if l > 62 else None
            record['ConservPredTFBS']               = f[62] if l > 63 else None
            record['HumanEnhancer']                 = f[63] if l > 64 else None
            record['RNAedit']                       = f[64] if l > 65 else None
            record['PolyPhen2']                     = f[65] if l > 66 else None
            record['SIFT']                          = f[66] if l > 67 else None
            record['LSSNP']                         = f[67] if l > 68 else None
            record['UniProt']                       = f[68] if l > 69 else None
            record['EqtlMethMetabStudy']            = f[69] if l > 70 else None
            snp_records.append(record)

            # Create association records
            for i in our_phenos:
                phassoc_records.append({'snp_id' : sid, 'pheno_id' : i})
            for i in our_platforms:
                plassoc_records.append({'snp_id' : sid, 'platform_id' : i})

            # Decide when to execute
            if count:
                count -= 1
            else:
                if progress:
                    tqdm.write('Writing rows...')
                else:
                    sys.stdout.write('Writing rows...\n')
                conn.execute(snp_ins, snp_records)
                conn.execute(phassoc_ins, phassoc_records)
                conn.execute(plassoc_ins, plassoc_records)
                if progress:
                    tqdm.write('{} rows written'.format(rows))
                else:
                    sys.stdout.write('{} rows written\n'.format(rows))
                count           = 49999
                snp_records     = []
                phassoc_records = []
                plassoc_records = []
            rows += 1
            if progress:
                pbar.update()

        # Final insert
        sys.stdout.write('Writing final rows...\n')
        conn.execute(snp_ins, snp_records)
        conn.execute(phassoc_ins, phassoc_records)
        conn.execute(plassoc_ins, plassoc_records)
        sys.stdout.write('{} rows written\n'.format(rows))
        sys.stdout.write('Done!\n')


###############################################################################
#                              Support Functions                              #
###############################################################################


def split_messy_list(string):
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
    return final_list


def get_date(string):
    """Return datetime date object from string."""
    return date.fromordinal(dateparse(string).toordinal())


def get_bool(string):
    """Return a bool from a string of y/n."""
    string = string.lower()
    return True if string == 'y' else False


def open_zipped(infile, mode='r', encoding='utf-8'):
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
