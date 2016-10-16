"""
A Simple GRASP (grasp.nhlbi.nih.gov) API based on SQLAlchemy and Pandas
"""

# Version Number
__version__ = '0.2.0b'

# Import ourself
from . import db
from . import ref
from . import query
from . import tables
from .db import get_session
from .tables import SNP, Phenotype, PhenoCats, Platform, Population
from .query import get_studies, get_snps

__all__ = ["tables", "query", "get_session", "get_studies", "get_snps"]

