"""
A Simple GRASP (grasp.nhlbi.nih.gov) API based on SQLAlchemy and Pandas
"""

# Version Number
__version__ = '0.3.0b2'

# Import ourself
from . import db
from . import ref
from . import query
from . import tables
from .db import get_session
from .tables import SNP, Phenotype, PhenoCats, Platform, Population
from .query import get_studies, get_snps

t = tables
q = query

__all__ = ['t', 'q', "tables", "query", "get_session", "get_studies",
           "get_snps", "SNP", "Phenotype", "PhenoCats", "Platform",
           "Population"]

