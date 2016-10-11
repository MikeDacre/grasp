"""
A mix of functions to make querying the database faster.

       Created: 2016-49-11 07:10
 Last modified: 2016-10-11 13:34

"""
import pandas as pd

from . import db
from . import tables as t

def get_pheno_pop_snps(pheno, pop, pandas=True):
    """Return a list of SNPs in a single population in a single phenotype.

    :pheno:   The phenotype of interest.
    :pop:     The population of interest.
    :pandas:  Return a dataframe instead of a list of SNP objects.
    :returns: Either a DataFrame or list of SNP objects.

    """
    s, e = db.get_session()
    pheno = s.query(t.Phenotype).filter(
        t.Phenotype.category == pheno).first()
    if pandas:
        return pd.read_sql(
            s.query(
                t.SNP.id, t.SNP.chrom, t.SNP.pos, t.SNP.pval
            ).filter(
                t.SNP.study_id.in_(
                    [i.id for i in pheno.studies
                     if i.population.population == pop]
                )
            ).statement, e, index_col='id')
    else:
        return s.query(t.SNP).filter(
            t.SNP.study_id.in_(
                [i.id for i in pheno.studies
                    if i.population.population == pop]
            )
        ).all()
