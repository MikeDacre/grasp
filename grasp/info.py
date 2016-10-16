"""
Little functions to pretty print column lists and category info.

get_{phenotypes,phenotype_categories,popululations} all display a dump of the
whole database.

get_population_flags displays available flags from PopFlag.

display_{study,snp}_columns displays a list of available columns in those two
tables as a formatted string.

get_{study,snp}_columns return a list of available columns in those two
tables as python objects.
"""
from tabulate import tabulate as _tb

# Us
from . import db as _db
from . import ref as _ref
from . import tables as t

###############################################################################
#                          Get Category Information                           #
###############################################################################


def get_phenotypes(list_only=False, dictionary=False, table=False):
    """Return all phenotypes from the Phenotype table.

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
    """Return all populatons from the Population table.

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


###############################################################################
#                           Get Column Information                            #
###############################################################################


def display_snp_columns(display_as='table', write=False):
    """Return all columns in the SNP table as a string.

    Display choices:
        table:      A formatted grid-like table
        tab:        A tab delimited non-formatted version of table
        list:       A string list of column names

    Args:
        display_as: {table,tab,list}
        write:      If true, print output to console, otherwise return
                    string.

    Returns:
        A formatted string or None
    """
    return t.SNP.display_columns(display_as, write)


def get_snp_columns(return_as='list'):
    """Return all columns in the SNP table.

    Display choices:
        list:       A python list of column names
        dictionary: A python dictionary of name=>desc
        long_dict:  A python dictionary of name=>(type, desc)

    Args:
        return_as:  {table,tab,list,dictionary,long_dict,id_dict}

    Returns:
        A list or dictionary
    """
    return t.SNP.get_columns(return_as)


def display_study_columns(display_as='table', write=False):
    """Return all columns in the Study table as a string.

    Display choices:
        table:      A formatted grid-like table
        tab:        A tab delimited non-formatted version of table
        list:       A string list of column names

    Args:
        display_as: {table,tab,list}
        write:      If true, print output to console, otherwise return
                    string.

    Returns:
        A formatted string or None
    """
    return t.Study.display_columns(display_as, write)


def get_study_columns(return_as='list'):
    """Return all columns in the SNP table.

    Display choices:
        list:       A python list of column names
        dictionary: A python dictionary of name=>desc
        long_dict:  A python dictionary of name=>(type, desc)

    Args:
        return_as:  {table,tab,list,dictionary,long_dict,id_dict}

    Returns:
        A list or dictionary
    """
    return t.Study.get_columns(return_as)
