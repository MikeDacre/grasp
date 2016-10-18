"""
A Simple GRASP (grasp.nhlbi.nih.gov) API based on SQLAlchemy and Pandas
"""

# Version Number
__version__ = '0.3.0b2'

# Make sure we can import the important stuff
# We don't check for modules required for initialization here
import tabulate as _
import pandas as _
import sqlalchemy as _
import myvariant as _
import flags as _
try:
    from flags import FlagsMeta as _
except ImportError:
    raise ImportError('Could not import py-flags. Make sure py-flags is ' +
                      'installed instead of pyflags (the hyphen is important)')


# Import ourself
from . import db
from . import ref
from . import query
from . import tables
from .db import get_session
from .ref import PopFlag
from .tables import SNP, Phenotype, PhenoCats, Platform, Population
from .query import get_studies, get_snps

t = tables
q = query

__all__ = ['t', 'q', "tables", "query", "get_session", "get_studies",
           "get_snps", "SNP", "Phenotype", "PhenoCats", "Platform",
           "Population", "PopFlag"]

