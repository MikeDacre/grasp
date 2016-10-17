"""
A mix of functions to make querying the database and analyzing the results
faster.
"""
from time import sleep as _sleep

import pandas as _pd
import myvariant as _mv

from . import db as _db
from . import ref as _ref
from . import tables as t

__all__ = ["get_studies", "get_snps", "get_variant_info",
           "find_intersecting_phenotypes", "collapse_dataframe",
           "intersect_overlapping_series"]


###############################################################################
#                        Retrieve SNPs and Study Data                         #
###############################################################################


def get_studies(primary_phenotype=None, pheno_cats=None, pheno_cats_alias=None,
                primary_pop=None, has_disc_pop=None, has_rep_pop=None,
                only_disc_pop=None, only_rep_pop=None, query=False,
                count=False, dictionary=False, pandas=False):
    """Return a list of studies filtered by phenotype and population.

    There are two ways to query both phenotype and population.

    Phenotype:
        GRASP provides a 'primary phenotype' for each study, which are fairly
        poorly curated. They also provide a list of phenotype categories, which
        are well curated. The problem with the categories is that there are
        multiple per study and some are to general to be useful. If using
        categories be sure to post filter the study list.

        Note: I have made a list of aliases for the phenotype categories to
        make them easier to type. Use pheno_cats_alias for that.

    Population:
        Each study has a primary population (list available with
        'get_populations') but some studies also have other populations in the
        cohort. GRASP indexes all population counts, so those can be used to
        query also. To query these use `has_` or `only_` (exclusive) parameters,
        you can query either discovery populations or replication populations.
        Note that you cannot provide both `has_` and `only_` parameters for the
        same population type.

        For doing population specific analyses most of the time you will want
        the excl_disc_pop query.

    Argument Description:
        Phenotype Arguments are 'primary_phenotype', 'pheno_cats', and
        'pheno_cats_alias'.

        Only provide one of pheno_cats or pheno_cats_alias

        Population Arguments are `primary_pop`, `has_disc_pop`, `has_rep_pop`,
        `only_disc_pop`, `only_rep_pop`.

        `primary_pop` is a simple argument, the others use bitwise flags for
        lookup.

        The easiest way to use the following parameters is with the
        _ref.PopFlag object. It uses py-flags. For example::

            pops = _ref.PopFlag.eur | _ref.PopFlag.afr

        In addition you can provide a list of strings correcponding to PopFlag
        attributes.

        Note: the `only_` parameters work as ANDs, not ORs. So
        only_disc_pop='eur|afr' will return those studies that have BOTH
        european and african discovery populations, but no other discovery
        populations. On the other hand, `has_` works as an OR, and will return
        any study with any of the spefified populations.

    Args:
        primary_phenotype: Phenotype of interest, string or list of strings.
        pheno_cats:        Phenotype category of interest.
        pheno_cats_alias:  Phenotype category of interest.

        primary_pop:       Query the primary population, string or list of
                           strings.

        has_disc_pop:      Return all studies with these discovery populations
        has_rep_pop:       Return all studies with these replication
                           populations
        only_disc_pop:     Return all studies with ONLY these discovery
                           populations
        only_rep_pop:      Return all studies with ONLY these replication
                           populations

        query:             Return the query instead of the list of study
                           objects.
        count:             Return a count of the number of studies.
        dictionary:        Return a dictionary of title->id for filtering.
        pandas:            Return a dataframe of study information instead
                           of the list.

    Returns:
        A list of study objects, a query, or a dataframe.

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
    elif dictionary:
        return {i.title: i.id for i in q.all()}
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
    if isinstance(studies, dict):
        studies = list(studies.values())
    if not isinstance(studies, (list, tuple)):
        studies = [studies]
    if isinstance(studies[0], t.Study):
        studies = [i.id for i in studies]
    studies = list(studies)

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


def lookup_rsid(rsid, study=False, columns=None, pandas=False):
    """Query database by rsID.

    Args:
        rsID (str):     An rsID or list of rsIDs
        study (bool):   Include study info in the output.
        columns (list): A list of columns to include in the query. Default is
                        all. List must be made up of column objects, e.g.
                        [t.SNP.snpid, t.Study.id]
        pandas (bool):  Return a dataframe instead of a list of SNPs

    Returns:
        list: List of SNP objects
    """
    s, e = _db.get_session()
    if not columns:
        columns = [t.SNP, t.Study] if study else [t.SNP]

    q = s.query(*columns)
    if study:
        q = q.filter(
            t.SNP.study_id == t.Study.id
        )

    if isinstance(rsid, str):
        q = q.filter(t.SNP.study_snpid == rsid)
    elif isinstance(rsid, (list, tuple)):
        q = q.filter(t.SNP.study_snpid.in_(rsid))
    else:
        raise ValueError('rsid must be either list or string')

    if pandas:
        return _pd.read_sql(q.statement, e, index_col='study_snpid')
    else:
        if isinstance(rsid, str):
            return q.first()
        else:
            return q.all()


def lookup_location(chrom, position, study=False, columns=None, pandas=False):
    """Query database by location.

    Args:
        chrom (str):    The chromosome as an int or string (e.g. 1 or chr1)
        position (int): Either one location, a list of locations, or a range
                        of locations, range can be expressed as a tuple of two
                        ints, a range object, or a string of 'int-int'
        study (bool):   Include study info in the output.
        columns (list): A list of columns to include in the query. Default is
                        all. List must be made up of column objects, e.g.
                        [t.SNP.snpid, t.Study.id]
        pandas (bool):  Return a dataframe instead of a list of SNPs

    Returns:
        list: List of SNP objects
    """
    s, e = _db.get_session()
    if isinstance(chrom, str) and chrom.startswith('chr'):
        chrom = chrom[3:]
    chrom = str(chrom)

    if not columns:
        columns = [t.SNP, t.Study] if study else [t.SNP]

    if study:
        q = s.query(*columns).filter(
            t.SNP.chrom == chrom
        ).filter(
            t.SNP.study_id == t.Study.id
        )
    else:
        q = s.query(*columns).filter(
            t.SNP.chrom == chrom
        )

    if isinstance(position, int):
        q = q.filter(t.SNP.pos == position)
    elif isinstance(position, list):
        q = q.filter(t.SNP.pos.in_(position))
    elif isinstance(position, str):
        if position.isdigit():
            q = q.filter(t.SNP.pos == int(position))
        else:
            start, end = position.split('-')
            q = q.filter(t.SNP.pos.between(int(start), int(end)))
    elif isinstance(position, range):
        print(position.start, position.stop)
        q = q.filter(t.SNP.pos.between(position.start, position.stop))
    elif isinstance(position, tuple):
        assert len(position) == 2
        q = q.filter(t.SNP.pos.between(int(position[0]), int(position[1])))
    else:
        raise ValueError("'position' must be an int, str, range, list, or " +
                         "tuple. Is {}".format(type(position)))

    if pandas:
        return _pd.read_sql(q.statement, e, index_col='study_snpid')
    else:
        if isinstance(position, int):
            return q.first()
        else:
            return q.all()


def find_intersecting_phenotypes(primary_pops=None, pop_flags=None,
                                 check='cat', pop_type='disc',
                                 exclusive=False, list_only=False):
    """Return a list of phenotypes that are present in all populations.

    Can only provide one of primary_pops or pop_flags. pop_flags does a
    bitwise lookup, primary_pops quries the primary string only.

    By default this function returns a list of phenotype categories, if you
    want to check primary phenotypes instead, provide check='primary'.

    Args:
        primary_pops: A string or list of strings corresponing to the
                      `tables.Study.phenotype` column
        pop_flags:    A `ref.PopFlag` object or list of objects.
        check:        cat/primary either check categories or primary phenos.
        pop_type:     disc/rep Use with pop_flags only, check either
                      discovery or replication populations.
        exclusive:    Use with pop_flags only, do an excusive rather than
                      inclusion population search
        list_only:    Return a list of names only, rather than a list of
                      objects

    Returns:
        A list of `table.Phenotype` or `table.PhenoCat` objects, or a list of
        names if `list_only` is specified.

    """
    # Check arguments
    if primary_pops and pop_flags:
        raise KeywordError("Cannot specify both 'primary_pops' and " +
                           "'pop_flags'")
    if not primary_pops and not pop_flags:
        raise KeywordError("Must provide at least one of 'primary_pops' or " +
                           "'pop_flags'")
    if check not in ['cat', 'primary']:
        raise KeywordError("'check' must be one of ['cat', 'primary']")

    # Pick query type
    if pop_flags:
        if pop_type not in ['disc', 'rep']:
            raise KeywordError("'pop_type' must be one of ['disc', 'rep']")
        l = 'only' if exclusive else 'has'
        key = '{}_{}_pop'.format(l, pop_type)
        qpops = [get_pop_flags(i) for i in pop_flags]
    else:
        key = 'primary_pop'
        qpops = primary_pops

    # Check that we have an iterable
    if not isinstance(qpops, (list, tuple)):
        raise KeywordError('Population query must be a list or tuple')

    # Get phenotype lists and intersect to form a final set
    # We use IDs here because it makes the set intersection more robust
    final_set = set()
    for pop in qpops:
        p = []
        for i in get_studies(**{key: pop}):
            p += i.phenotype_cats if check == 'cat' else i.phenotype
        out = set([i.id for i in p])
        if not final_set:
            final_set  = out
        else:
            final_set &= out

    # Get the final phenotype list
    s, _ = _db.get_session()
    phenos = []
    for id_list in _chunks(list(final_set), 999):
        table = t.Phenotype if primary_pops else t.PhenoCats
        phenos += s.query(table).filter(table.id.in_(id_list)).all()

    # Return the list
    if list_only:
        return [i.category for i in phenos] if check == 'cat' \
            else [i.phenotype for i in phenos]
    else:
        return phenos


###############################################################################
#                              MyVariant Queries                              #
###############################################################################


def get_variant_info(snp_list, fields='dbsnp', pandas=True):
    """Get variant info for a list of SNPs.

    Args:
        snp_list: A list of SNP objects or SNP rsIDs
        fields:   Choose fields to display from:
                  `docs.myvariant.info/en/latest/doc/data.html#available-fields`_
                  Good choices are 'dbsnp', 'clinvar', or 'gwassnps'
                  Can also use 'grasp' to get a different version of this
                  info.
        pandas:   Return a dataframe instead of dictionary.

    Returns:
        A dictionary or a dataframe.
    """
    mv = _mv.MyVariantInfo()
    if isinstance(snp_list, _pd.DataFrame):
        try:
            snps = list(snp_list.study_snpid)
        except AttributeError:
            snps = list(snp_list.index)
    elif isinstance(snp_list[0], t.SNP):
        snps = [i.study_snpid for i in snp_list]
    else:
        snps = snp_list
    assert isinstance(snps, (list, tuple))
    dfs = []
    for q in _chunks(snps, 999):
        dfs.append(mv.querymany(q, scopes='dbsnp.rsid', fields=fields,
                                as_dataframe=pandas, df_index=True))
        if len(snps) > 999:
            _sleep(2)
    if pandas:
        return _pd.concat(dfs)
    else:
        if len(dfs) > 1:
            return dfs
        else:
            return dfs[0]


###############################################################################
#                           DataFrame Manipulations                           #
###############################################################################


def collapse_dataframe(df, mechanism='median', pvalue_filter=None,
                       protected_columns=None):
    """Collapse a dataframe by chrom:location from get_snps.

    Will use the mechanism defined by 'mechanism' to collapse a dataframe
    to one indexed by 'chrom:location' with pvalue and count only.

    This function is agnostic to all dataframe columns other than::

        ['chrom', 'pos', 'snpid', 'pval']

    All other columns are collapsed into a comma separated list, a string.
    'chrom' and 'pos' are merged to become the new colon-separated index,
    snpid is maintained, and pval is merged using the function in 'mechanism'.

    Args:
        df:                A pandas dataframe, must have 'chrom', 'pos',
                           'snpid', and 'pval' columns.
        mechanism:         A numpy statistical function to use to collapse the
                           pvalue, median or mean are the common ones.
        pvalue_filter:     After collapsing the dataframe, filte to only
                           include pvalues less than this cutoff.
        protected_columns: A list of column names that will be maintened as is,
                           although all duplicates will be dropped (randomly).
                           Only makes sense for columns that are identical
                           for all studies of the same SNP.

    Returns:
        DataFrame: Indexed by chr:pos, contains flattened pvalue column, and
                   all original columns as a comma-separated list. Additionally
                   contains a count and stddev (of pvalues) column. stddev is
                   nan if count is 1.

    """
    # Copy the dataframe to avoid clobbering it
    df = df.sort_values(['chrom', 'pos'])

    # Add the location column, which will become the index
    df['location'] = df.apply(_create_loc, axis=1)

    # Move all of the columns we want to maintain to a separate df and drop
    # dups
    if protected_columns:
        prot_cols = []
        for i in protected_columns:
            if i not in ['location', 'snpid', 'chrom', 'pos', 'pval']:
                prot_cols.append(i)
        df_prot = df[prot_cols]
        df_prot = df_prot.drop_duplicates('location')
        df_prot.set_index('location', inplace=True)
        df.drop(prot_cols, axis=1, inplace=True)

    # Protect SNPID, chrom, and location
    df_snp = df[['location', 'snpid', 'chrom', 'pos']]
    df_snp = df_snp.drop_duplicates('location')
    df_snp.set_index('location', inplace=True)
    df.drop(['snpid', 'chrom', 'pos'], axis=1, inplace=True)

    # Flatten the pvalue
    df_p = df[['location', 'pval']]
    df.drop('pval', axis=1, inplace=True)
    df_p = df_p.groupby('location').aggregate([mechanism, 'std', 'count'])
    df_p.columns = ['pval', 'std', 'count']

    # Flatten the remainder
    df = df.groupby('location').aggregate(_aggregate_strings)

    # Recombine
    comb_list = [df_snp, df_p, df]
    if protected_columns:
        comb_list.insert(2, df_prot)

    df = _pd.concat(comb_list, axis=1)

    # Filter
    if pvalue_filter:
        df = df[df.pval < pvalue_filter]

    # Done
    return df


def intersect_overlapping_series(series1, series2, names=None,
                                 stats=True, plot=False):
    """Plot all SNPs that overlap between two pvalue series.

    Args:
        series: A pandas series object
        names:  A list of two names to use for the resultant dataframes
        stats:  Print some stats on the intersection
        plot:   Plot the resulting intersection

    Returns:
        DataFrame: with the two series as columns
    """
    if isinstance(series1, _pd.DataFrame):
        series1 = series1.pval
    if isinstance(series2, _pd.DataFrame):
        series2 = series2.pval
    assert isinstance(series1, _pd.Series)
    assert isinstance(series2, _pd.Series)

    df = _pd.concat([series1, series2], join='inner', axis=1)
    names = names if names else ['series1', 'series2']

    assert isinstance(names, list)

    df.columns = names

    if stats:
        print("Series 1 len: {}".format(len(series1)))
        print("Series 2 len: {}".format(len(series2)))
        print("Intersected df len: {}".format(len(df)))

    if plot:
        df.plot()

    return df


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


def _aggregate_strings(x):
    """Converts records to comma separated string."""
    return ','.join(set([str(i) for i in x]))


def _create_loc(x):
    """Merge chrom and pos columns into 'chrom:pos'."""
    return '{}:{}'.format(x.chrom, x.pos)


def _chunks(l, n):
    n = max(1, n)
    return (l[i:i+n] for i in range(0, len(l), n))


###############################################################################
#                            Exception Definition                             #
###############################################################################


class KeywordError(Exception):

    """For incorrect combinations of arguments."""

    pass
