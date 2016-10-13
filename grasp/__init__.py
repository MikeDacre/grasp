"""
A Simple GRASP (grasp.nhlbi.nih.gov) API based on SQLAlchemy and Pandas
"""
# Version Number
__version__ = '0.1.2a'

# Import ourself
from . import tables
from . import db
from .tables import SNP, Phenotype, Platform, Population

__all__ = ["tables", "db"]
