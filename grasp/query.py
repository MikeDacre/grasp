"""
A mix of functions to make querying the database faster.

       Created: 2016-49-11 07:10
 Last modified: 2016-10-14 13:20

"""
import pandas as _pd

from . import db as _db
from . import tables as t

__all__ = ["get_studies", "get_snps", "get_phenotypes", "get_populations"]


###############################################################################
#                        Retrieve SNPs and Study Data                         #
###############################################################################


def get_studies(pheno=None, pop=None):
    """Return a list of studies filtered by phenotype and population.

    :pheno:   The phenotype of interest, string or list of strings.
    :pop:     The population of interest, string or list of strings.
    :returns: A list of studies.

    """
    s, _ = _db.get_session()

    if pheno and isinstance(pheno, str):
        pheno = [pheno]
    if pop and isinstance(pop, str):
        pop = [pop]
    if pheno:
        phenos = s.query(t.Phenotype).filter(
            t.Phenotype.category.in_(pheno)).all()
        if pop:
            return [i for i in phenos.studies
                    if i.population.population in pop]
        else:
            return [i for i in phenos.studies]
    elif pop:
        pops = s.query(t.Population).filter(
            t.Population.population.in_(pop)).all()
        return [i for i in pops.studies]


def get_snps(studies, pandas=True):
    """Return a list of SNPs in a single population in a single phenotype.

    :studies: A list of studies.
    :pandas:  Return a dataframe instead of a list of SNP objects.
    :returns: Either a DataFrame or list of SNP objects.

    """
    s, e = _db.get_session()
    if isinstance(studies[0], t.Study):
        studies = [i.id for i in studies]

    if pandas:
        return _pd.read_sql(
            s.query(
                t.SNP.id, t.SNP.chrom, t.SNP.pos, t.SNP.snpid,
                t.SNP.study_snpid, t.SNP.pval, t.SNP.study_id, t.SNP.InGene,
                t.SNP.InMiRNA, t.SNP.InLincRNA, t.SNP.LSSNP,
                t.SNP.primary_pheno, t.SNP.population_id
            ).filter(
                t.SNP.study_id.in_(studies)
            ).statement, e, index_col='id')
    else:
        return s.query(t.SNP).filter(
            t.SNP.study_id.in_(studies)
        ).all()

###############################################################################
#                          Get Category Information                           #
###############################################################################


def get_phenotypes(list_only=False, dictionary=False):
    """Return all phenotypes from the phenotype table.

    :list_only:  Return a simple text list instead of a list of Phenotype
                 objects.
    :dictionary: Return a dictionary of phenotype=>ID
    """
    s, _ = _db.get_session()
    q = s.query(t.Phenotype).order_by('category').all()
    if list_only:
        return [i.category for i in q]
    elif dictionary:
        return {i.category: i.id for i in q}
    else:
        return q


def get_populations(list_only=False, dictionary=False):
    """Return all phenotypes from the phenotype table.

    :list_only:  Return a simple text list instead of a list of Phenotype
                 objects.
    :dictionary: Return a dictionary of population=>ID
    """
    s, _ = _db.get_session()
    q =  s.query(t.Population).all()
    if list_only:
        return [i.population for i in q]
    elif dictionary:
        return {i.population: i.id for i in q}
    else:
        return q
