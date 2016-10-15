"""
A mix of functions to make querying the database faster.

       Created: 2016-49-11 07:10
 Last modified: 2016-10-14 19:15

"""
import pandas as _pd

from . import db as _db
from . import tables as t

__all__ = ["get_studies", "get_snps", "get_phenotypes", "get_populations"]


###############################################################################
#                        Retrieve SNPs and Study Data                         #
###############################################################################


def get_studies(primary_phenotype=None, pheno_cats=None):
    """Return a list of studies filtered by phenotype and population.

    There are two ways to query both phenotype and population.

    Phenotype
    ---------

    GRASP provides a 'primary phenotype' for each study, which are fairly
    poorly curated. They also provide a list of phenotype categories, which
    are well curated. The problem with the categories is that there are
    multiple per study and some are to general to be useful. If using
    categories be sure to post filter the study list.

    Population
    ----------

    Each study has a primary population (list available with 'get_populations')
    but some studies also have other populations in the cohort. GRASP indexes
    all population counts, so those can be used to query also. To query these
    use has_ or excl_ (exclusive) parameters, you can query either discovery
    populations or replication populations. Note that you cannot provide both
    has_ and excl_ parameters for the same population type.

    For doing population specific analyses most of the time you will want the
    excl_disc_pop query.

    Params
    ------

    Pheno
    .....

    :primary_phenotype: Phenotype of interest, string or list of strings.
    :pheno_cats:        Phenotype category of interest.

    Pop
    ...

    :primary_pop:  Query the primary population, string or list of strings.

    The following parameters can take a string or a ref.PopFlag parameter.

    :has_disc_pop:  Return all studies with these discovery populations
    :has_rep_pop:   Return all studies with these replication populations
    :only_disc_pop: Return all studies with ONLY these discovery populations
    :only_rep_pop:  Return all studies with ONLY these replication populations

    General
    .......

    :query:   Return the query instead of the list of study objects.
    :pandas:  Return a dataframe of study information instead of the list.
    :returns: A list of study objects, a query, or a dataframe.

    """
    s, _ = _db.get_session()

    if (has_disc_pop and excl_disc_pop) or (has_rep_pop and excl_rep_pop)
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
#                      Use MyVariant to get Variant Info                      #
###############################################################################


def get_variant_info(snp_list, fields="dbsnp", pandas=True):
    """Use the myvariant API to get info about this SNP.

    Note that this service can be very slow.

    :snp_list: A list of SNP objects or 'chr:loc'
    :fields:   Choose fields to display from:
                  docs.myvariant.info/en/latest/doc/data.html#available-fields
                  Good choices are 'dbsnp', 'clinvar', or 'gwassnps'
                  Can also use 'grasp' to get a different version of this info.
    :pandas:   Return a dataframe instead of dictionary.
    """
    mv = myvariant.MyVariantInfo()
    if isinstance(snp_list[0], t.SNP):
        snp_list = [i.snp_loc for i in snp_list]
    return mv.querymany(snp_list, fields=fields, as_dataframe=pandas,
                        df_index=True)

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
