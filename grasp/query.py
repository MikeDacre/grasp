"""
A mix of functions to make querying the database faster.

       Created: 2016-49-11 07:10
 Last modified: 2016-10-11 14:15

"""
import pandas as pd

from . import db
from . import tables as t

def get_pheno_pop_snps(pheno, pop='', pandas=True):
    """Return a list of SNPs in a single population in a single phenotype.

    :pheno:   The phenotype of interest or a filtered study list.
    :pop:     The population of interest.
    :pandas:  Return a dataframe instead of a list of SNP objects.
    :returns: Either a DataFrame or list of SNP objects.

    """
    s, e = db.get_session()
    if isinstance(pheno, list):
        if isinstance(pheno[0], t.Study):
            studies = [i.id for i in pheno
                       if i.population.population == pop]
    else:
        phenos = s.query(t.Phenotype).filter(
            t.Phenotype.category == pheno).first()
        studies = [i.id for i in phenos.studies
                   if i.population.population == pop]
    if pandas:
        return pd.read_sql(
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
