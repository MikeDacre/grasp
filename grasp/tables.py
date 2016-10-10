"""
Table descriptions in SQLAlchemy ORM.

       Created: 2016-10-08
 Last modified: 2016-10-10 12:13

"""
from sqlalchemy import Table, Column, Index, ForeignKey
from sqlalchemy import Integer, String, Float, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

__all__ = ["SNP", "Phenotype", "Platform", "Population"]

Base = declarative_base()

###############################################################################
#                             Association Tables                              #
###############################################################################

pheno_assoc_table = Table(
    'pheno_association', Base.metadata,
    Column('snp_id', Integer, ForeignKey('snps.id')),
    Column('pheno_id', Integer, ForeignKey('phenos.id'))
)

plat_assoc_table = Table(
    'platform_association', Base.metadata,
    Column('snp_id', Integer, ForeignKey('snps.id')),
    Column('platform_id', Integer, ForeignKey('platforms.id'))
)


###############################################################################
#                               Database Tables                               #
###############################################################################


class SNP(Base):

    """An SQLAlchemy Talble for GRASP SNPs"""

    __tablename__ = "snps"

    id                          = Column(Integer, primary_key=True, index=True)
    SNPid                       = Column(String, index=True)
    chrom                       = Column(String, index=True)
    pos                         = Column(Integer, index=True)
    HUPfield                    = Column(String)
    LastCurationDate            = Column(Date)
    CreationDate                = Column(Date)
    PMID                        = Column(String)
    SNPid_paper                 = Column(String)
    LocationWithinPaper         = Column(String)
    Pvalue                      = Column(Float)
    Phenotype                   = Column(String)
    PaperPhenotypeDescription   = Column(String)
    phenotypes                  = relationship("Phenotype",
                                               secondary=pheno_assoc_table,
                                               back_populates="snps")
    DatePub                     = Column(Date)
    InNHGRIcat                  = Column(Boolean)
    Journal                     = Column(String)
    Title                       = Column(String)
    MF_analysis                 = Column(Boolean)
    MF_analysis_exclusive       = Column(Boolean)
    sample_desc                 = Column(String)
    rep_sample_desc             = Column(String)
    platforms                   = relationship("Platform",
                                               secondary=plat_assoc_table,
                                               back_populates="snps")
    snp_count                   = Column(String)
    imputed                     = Column(Boolean)
    population_desc             = Column(String,
                                         ForeignKey('populations.population'))
    population                  = relationship("Population",
                                               backref="snps")
    TotalSamples                = Column(Integer)
    TotalDiscoverySamples       = Column(Integer)
    EuropeanDiscovery           = Column(Integer)
    AfricanDiscovery            = Column(Integer)
    EastAsianDiscovery          = Column(String)
    IndianSouthAsianDiscovery   = Column(String)
    HispanicDiscovery           = Column(String)
    NativeDiscovery             = Column(String)
    MicronesianDiscovery        = Column(String)
    ArabMEDiscovery             = Column(String)
    MixedDiscovery              = Column(String)
    UnspecifiedDiscovery        = Column(String)
    FilipinoDiscovery           = Column(String)
    IndonesianDiscovery         = Column(String)
    Totalreplicationsamples     = Column(String)
    EuropeanReplication         = Column(String)
    AfricanReplication          = Column(String)
    EastAsianReplication        = Column(String)
    IndianSouthAsianReplication = Column(String)
    HispanicReplication         = Column(String)
    NativeReplication           = Column(String)
    MicronesianReplication      = Column(String)
    ArabMEReplication           = Column(String)
    MixedReplication            = Column(String)
    UnspecifiedReplication      = Column(String)
    FilipinoReplication         = Column(String)
    IndonesianReplication       = Column(String)
    InGene                      = Column(String)
    NearestGene                 = Column(String)
    InLincRNA                   = Column(String)
    InMiRNA                     = Column(String)
    InMiRNABS                   = Column(String)
    dbSNPfxn                    = Column(String)
    dbSNPMAF                    = Column(String)
    dbSNPalleles                = Column(String)
    dbSNPvalidation             = Column(String)
    dbSNPClinStatus             = Column(String)
    ORegAnno                    = Column(String)
    ConservPredTFBS             = Column(String)
    HumanEnhancer               = Column(String)
    RNAedit                     = Column(String)
    PolyPhen2                   = Column(String)
    SIFT                        = Column(String)
    LSSNP                       = Column(String)
    UniProt                     = Column(String)
    EqtlMethMetabStudy          = Column(String)

    Index('chrom_pos', 'chrom', 'pos')

    def __repr__(self):
        """Display information about the table."""
        return "{} ({}) <{}:{} pheno: {} total: {} EUR: {} AFR: {}".format(
            self.id, self.SNPid, self.chrom, self.pos, self.Phenotype,
            self.TotalSamples, self.EuropeanDiscovery, self.AfricanDiscovery)


class Phenotype(Base):

    """To store the lists of phenotype categories."""

    __tablename__ = "phenos"

    id       = Column(Integer, primary_key=True, autoincrement=True,
                      index=True)
    category = Column(String, index=True, unique=True)
    snps     = relationship("SNP",
                            secondary=pheno_assoc_table,
                            back_populates="phenotypes")

    def __init__(self, category):
        """Create self."""
        self.category = category

    def __repr__(self):
        """Display information."""
        return "{} <{}>".format(self.id, self.category)


class Platform(Base):

    """To store the platform information."""

    __tablename__ = "platforms"

    id       = Column(Integer, primary_key=True, autoincrement=True,
                      index=True)
    platform = Column(String, index=True, unique=True)
    snps     = relationship("SNP",
                            secondary=plat_assoc_table,
                            back_populates="platforms")

    def __init__(self, platform):
        """Create self."""
        self.platform = platform

    def __repr__(self):
        """Display information."""
        return "{} <{}>".format(self.id, self.platform)


class Population(Base):

    """To store the platform information."""

    __tablename__ = "populations"

    id         = Column(Integer, primary_key=True, autoincrement=True,
                        index=True)
    population = Column(String, index=True, unique=True)

    def __init__(self, population):
        """Create self."""
        self.population = population

    def __repr__(self):
        """Display information."""
        return "{} <{}>".format(self.id, self.population)
