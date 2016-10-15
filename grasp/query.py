"""
A mix of functions to make querying the database faster.

       Created: 2016-49-11 07:10
 Last modified: 2016-10-15 02:00

"""
import pandas as _pd
import myvariant as _mv
from tabulate import tabulate as _tb

from . import db as _db
from . import ref as _ref
from . import tables as t

__all__ = ["get_studies", "get_snps", "get_phenotypes", "get_populations"]


###############################################################################
#                        Retrieve SNPs and Study Data                         #
###############################################################################


def get_studies(primary_phenotype=None, pheno_cats=None, pheno_cats_alias=None,
                primary_pop=None, has_disc_pop=None, has_rep_pop=None,
                only_disc_pop=None, only_rep_pop=None, query=False,
                count=False, pandas=False):
    """Return a list of studies filtered by phenotype and population.

    There are two ways to query both phenotype and population.

    Phenotype
    ---------

    GRASP provides a 'primary phenotype' for each study, which are fairly
    poorly curated. They also provide a list of phenotype categories, which
    are well curated. The problem with the categories is that there are
    multiple per study and some are to general to be useful. If using
    categories be sure to post filter the study list.

    Note: I have made a list of aliases for the phenotype categories to make
    them easier to type. Use pheno_cats_alias for that.

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
    :pheno_cats_alias:  Phenotype category of interest.

    Only provide one of pheno_cats or pheno_cats_alias

    Pop
    ...

    :primary_pop:  Query the primary population, string or list of strings.

    The easiest way to use the following parameters is with the _ref.PopFlag
    object. It uses py-flags. For example:
        pops = _ref.PopFlag.eur | _ref.PopFlag.afr

    In addition you can provide a list of strings correcponding to PopFlag
    attributes.

    :has_disc_pop:  Return all studies with these discovery populations
    :has_rep_pop:   Return all studies with these replication populations
    :only_disc_pop: Return all studies with ONLY these discovery populations
    :only_rep_pop:  Return all studies with ONLY these replication populations

    Note: the only_ parameters work as ANDs, not ORs. So
    only_disc_pop='eur|afr' will return those studies that have BOTH european
    and african discovery populations, but no other discovery populations. On
    the other hand, has_ works as an OR, and will return any study with any
    of the spefified populations.

    General
    .......

    :query:   Return the query instead of the list of study objects.
    :count:   Return a count of the number of studies.
    :pandas:  Return a dataframe of study information instead of the list.
    :returns: A list of study objects, a query, or a dataframe.

    """
    s, e = _db.get_session()

    if (has_disc_pop and only_disc_pop) or (has_rep_pop and only_rep_pop):
        raise KeywordError('Cannot use both has_ and only_ args')

    # Create a query, we will build it iteratively
    q = s.query(t.Study)

    # Phenotype queries
    if primary_phenotype:
        if isinstance(primary_phenotype, (list, tuple)):
            q = q.filter(
                t.Study.phenotype.has(
                    t.Phenotype.phenotype.in_(primary_phenotype)
                )
            )
        else:
            q = q.filter(t.Study.phenotype.has(phenotype=primary_phenotype))
    if pheno_cats:
        if isinstance(pheno_cats, (list, tuple)):
            q = q.filter(
                t.Study.phenotype_cats.any(
                    t.PhenoCats.category.in_(pheno_cats)
                )
            )
        else:
            q = q.filter(t.Study.phenotype_cats.any(category=pheno_cats))
    if pheno_cats_alias:
        if isinstance(pheno_cats, (list, tuple)):
            q = q.filter(
                t.Study.phenotype_cats.any(
                    t.PhenoCats.alias.in_(pheno_cats)
                )
            )
        else:
            q = q.filter(t.Study.phenotype_cats.any(alias=pheno_cats_alias))

    # Population queries
    if primary_pop:
        if isinstance(primary_pop, (list, tuple)):
            q = q.filter(
                t.Study.population.has(
                    t.Population.population.in_(primary_pop)
                )
            )
        else:
            q = q.filter(t.Study.population.has(population=primary_pop))

    # Bitwise population queries
    if has_disc_pop:
        pop_flags = get_pop_flags(has_disc_pop)
        q = q.filter(t.Study.disc_pop_flag.op('&')(int(pop_flags)) != 0)
    elif only_disc_pop:
        pop_flags = get_pop_flags(only_disc_pop)
        q = q.filter(
            t.Study.disc_pop_flag.op('&')(
                int(pop_flags)) == int(pop_flags))

    if has_rep_pop:
        pop_flags = get_pop_flags(has_rep_pop)
        q = q.filter(t.Study.disc_pop_flag.op('&')(int(pop_flags)) != 0)
    elif only_rep_pop:
        pop_flags = get_pop_flags(only_rep_pop)
        q = q.filter(
            t.Study.disc_pop_flag.op('&')(
                int(pop_flags)) == int(pop_flags))

    # Query is built, now we decide how to return it.
    if query:
        return q
    elif count:
        return q.count()
    elif pandas:
        return _pd.read_sql(q.statement, e)
    else:
        return q.all()


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
        dfs = []
        for small_studies in _chunks(studies, 999):
            dfs.append(_pd.read_sql(
                s.query(
                    t.SNP.id, t.SNP.chrom, t.SNP.pos, t.SNP.snpid,
                    t.SNP.study_snpid, t.SNP.pval, t.SNP.study_id, t.SNP.InGene,
                    t.SNP.InMiRNA, t.SNP.InLincRNA, t.SNP.LSSNP,
                    t.SNP.phenotype_desc
                ).filter(
                    t.SNP.study_id.in_(small_studies)
                ).statement, e, index_col='id'))
        return _pd.concat(dfs)
    else:
        snps = []
        for small_studies in _chunks(studies, 999):
            snps += s.query(t.SNP).filter(
                t.SNP.study_id.in_(small_studies)
            ).all()
        return snps

###############################################################################
#                              Helper Functions                               #
###############################################################################

def get_pop_flags(pop_flags):
    """Merge a list, string, int, or PopFlag series."""
    if isinstance(pop_flags, _ref.PopFlag):
        return pop_flags
    if not isinstance(pop_flags, (list, tuple)):
        pop_flags = [pop_flags]
    final_flag = _ref.PopFlag(0)
    for pflag in pop_flags:
        if isinstance(pflag, int):
            pflag = _ref.PopFlag(pflag)
        elif isinstance(pflag, str):
            pflag = _ref.PopFlag.from_simple_str(pflag)
        if isinstance(pflag, _ref.PopFlag):
            final_flag |= pflag
        else:
            raise TypeError('Could not convert population flag into PopFlag')
    return final_flag


def _chunks(l, n):
    n = max(1, n)
    return (l[i:i+n] for i in range(0, len(l), n))


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
    mv = _mv.MyVariantInfo()
    if isinstance(snp_list[0], t.SNP):
        snp_list = [i.snp_loc for i in snp_list]
    return mv.querymany(snp_list, fields=fields, as_dataframe=pandas,
                        df_index=True)

###############################################################################
#                          Get Category Information                           #
###############################################################################


def get_phenotypes(list_only=False, dictionary=False, table=False):
    """Return all phenotypes from the phenotype table.

    :list_only:  Return a simple text list instead of a list of Phenotype
                 objects.
    :dictionary: Return a dictionary of phenotype=>ID
    :table:      Return a pretty table for printing.
    """
    s, _ = _db.get_session()
    q = s.query(t.Phenotype).order_by('phenotype').all()
    if list_only:
        return [i.phenotype for i in q]
    elif dictionary:
        return {i.phenotype: i.id for i in q}
    elif table:
        ids    = [i.id for i in q]
        phenos = [i.phenotype for i in q]
        return _tb({'ID': ids, 'Phenotype': phenos}, headers='keys',
                   tablefmt='grid')
    else:
        return q


def get_phenotype_categories(list_only=False, dictionary=False, table=False):
    """Return all phenotype categories from the PhenoCats table.

    :list_only:  Return a simple text list instead of a list of Phenotype
                 objects.
    :dictionary: Return a dictionary of phenotype=>ID
    :table:      Return a pretty table for printing.
    """
    s, _ = _db.get_session()
    q = s.query(t.PhenoCats).order_by('category').all()
    if list_only:
        return [i.category for i in q]
    elif dictionary:
        return {i.category: i.id for i in q}
    elif table:
        ids     = [i.id for i in q]
        cats    = [i.category for i in q]
        aliases = [i.alias for i in q]
        return _tb({'ID': ids, 'Category': cats, 'Alias': aliases},
                   headers='keys', tablefmt='grid')
    else:
        return q


def get_populations(list_only=False, dictionary=False, table=False):
    """Return all phenotypes from the phenotype table.

    :list_only:  Return a simple text list instead of a list of Phenotype
                 objects.
    :dictionary: Return a dictionary of population=>ID
    :table:      Return a pretty table for printing.
    """
    s, _ = _db.get_session()
    q =  s.query(t.Population).all()
    if list_only:
        return [i.population for i in q]
    elif dictionary:
        return {i.population: i.id for i in q}
    elif table:
        ids  = [i.id for i in q]
        pops = [i.population for i in q]
        return _tb({'ID': ids, 'Population': pops}, headers='keys',
                   tablefmt='grid')
    else:
        return q


def get_population_flags(list_only=False, dictionary=False, table=False):
    """Return all population flags available in the PopFlags class.

    :list_only:  Return a simple text list instead of a list of Phenotype
                 objects.
    :dictionary: Return a dictionary of population=>ID
    :table:      Return a pretty table for printing.
    """
    flags = _ref.PopFlag.__dict__['__members__']
    if list_only:
        return [i for i in flags.values()]
    elif dictionary:
        return {k: v for k, v in flags.items()}
    elif table:
        return _tb(
            [['FLAG', 'Label']] + [[int(v), k] for k, v in flags.items()],
            headers='firstrow', tablefmt='grid'
        )
    else:
        return flags


def get_study_columns(list_only=False, dictionary=False, table=False):
    """Return all columns in the Study table.

    :list_only:  Return a simple text list instead of a list of Phenotype
                 objects.
    :dictionary: Return a dictionary of population=>ID
    :table:      Return a pretty table for printing.
    """
    cols = t.Study.columns
    if list_only:
        return [i[1] for i in cols.values()]
    elif dictionary:
        return {k: v[1] for k, v in cols.items()}
    elif table:
        return _tb(
            [['Column', 'Description', 'Type']] +\
            [[k, v[1], v[0]] for k, v in cols.items()],
            headers='firstrow', tablefmt='grid'
        )
    else:
        return cols


def get_snp_columns(list_only=False, dictionary=False, table=False):
    """Return all columns in the SNP table.

    :list_only:  Return a simple text list instead of a list of Phenotype
                 objects.
    :dictionary: Return a dictionary of population=>ID
    :table:      Return a pretty table for printing.
    """
    cols = t.SNP.columns
    if list_only:
        return [i[1] for i in cols.values()]
    elif dictionary:
        return {k: v[1] for k, v in cols.items()}
    elif table:
        return _tb(
            [['Column', 'Description', 'Type']] +\
            [[k, v[1], v[0]] for k, v in cols.items()],
            headers='firstrow', tablefmt='grid'
        )
    else:
        return cols


###############################################################################
#                            Exception Definition                             #
###############################################################################


class KeywordError(Exception):

    """For incorrect combinations of arguments."""

    pass
