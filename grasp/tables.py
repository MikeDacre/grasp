"""
Table descriptions in SQLAlchemy ORM.

       Created: 2016-10-08
 Last modified: 2016-10-14 09:07

"""
from sqlalchemy import Table, Column, Index, ForeignKey
from sqlalchemy import BigInteger, Integer, String, Float, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

__all__ = ["SNP", "Phenotype", "PhenoCats", "Platform", "Population"]

Base = declarative_base()


###############################################################################
#                             Association Tables                              #
###############################################################################

snp_pheno_assoc = Table(
    'snp_pheno_association', Base.metadata,
    Column('snp_id', BigInteger, ForeignKey('snps.id')),
    Column('pheno_id', Integer, ForeignKey('pheno_cats.id'))
)

study_pheno_assoc = Table(
    'study_pheno_association', Base.metadata,
    Column('study_id', Integer, ForeignKey('studies.id')),
    Column('pheno_id', Integer, ForeignKey('pheno_cats.id'))
)

study_plat_assoc = Table(
    'study_platform_association', Base.metadata,
    Column('study_id', Integer, ForeignKey('studies.id')),
    Column('platform_id', Integer, ForeignKey('platforms.id'))
)


###############################################################################
#                               Database Tables                               #
###############################################################################


class SNP(Base):

    """An SQLAlchemy Talble for GRASP SNPs"""

    __tablename__ = "snps"

    id                 = Column(BigInteger, primary_key=True, index=True)
    snpid              = Column(String, index=True)
    chrom              = Column(String(10), index=True)
    pos                = Column(Integer, index=True)
    pval               = Column(Float, index=True)
    NHLBIkey           = Column(String, index=True)
    HUPfield           = Column(String)
    LastCurationDate   = Column(Date)
    CreationDate       = Column(Date)
    population_id      = Column(Integer, ForeignKey('populations.id'))
    population         = relationship("Population",
                                      backref="snps")
    study_id           = Column(Integer, ForeignKey('studies.id'))
    study              = relationship("Study",
                                      back_populates="snps")
    study_snpid        = Column(String)
    paper_loc          = Column(String)
    phenotype_desc     = Column(String, index=True)
    phenotype_cats     = relationship("PhenoCats",
                                      secondary=snp_pheno_assoc,
                                      back_populates="snps")
    InGene             = Column(String)
    NearestGene        = Column(String)
    InLincRNA          = Column(String)
    InMiRNA            = Column(String)
    InMiRNABS          = Column(String)
    dbSNPfxn           = Column(String)
    dbSNPMAF           = Column(String)
    dbSNPinfo          = Column(String)
    dbSNPvalidation    = Column(String)
    dbSNPClinStatus    = Column(String)
    ORegAnno           = Column(String)
    ConservPredTFBS    = Column(String)
    HumanEnhancer      = Column(String)
    RNAedit            = Column(String)
    PolyPhen2          = Column(String)
    SIFT               = Column(String)
    LSSNP              = Column(String)
    UniProt            = Column(String)
    EqtlMethMetabStudy = Column(String)

    Index('chrom_pos', 'chrom', 'pos')

    columns = {
        'id':                  'ID (generated from NHLBIKey)',
        'snpid':               'SNPid(dbSNP134)',
        'chrom':               'chr(hg19)',
        'pos':                 'pos(hg19)',
        'pval':                'Pvalue',
        'NHLBIkey':            'NHLBIkey',
        'HUPfield':            'HUPfield',
        'LastCurationDate':    'LastCurationDate',
        'CreationDate':        'CreationDate',
        'population_id':       'Primary key of population table',
        'population':          'Link to population table',
        'study_id':            'Primary key of the study table',
        'study':               'Link to study table',
        'study_snpid':         'SNPid(in paper)',
        'paper_loc':           'LocationWithinPaper',
        'primary_pheno':       'Phenotype',
        'phenotypes':          'Link to phenotypes',
        'InGene':              'InGene',
        'NearestGene':         'NearestGene',
        'InLincRNA':           'InLincRNA',
        'InMiRNA':             'InMiRNA',
        'InMiRNABS':           'InMiRNABS',
        'dbSNPfxn':            'dbSNPfxn',
        'dbSNPMAF':            'dbSNPMAF',
        'dbSNPinfo':           'dbSNPalleles/het/se',
        'dbSNPvalidation':     'dbSNPvalidation',
        'dbSNPClinStatus':     'dbSNPClinStatus',
        'ORegAnno':            'ORegAnno',
        'ConservPredTFBS':     'ConservPredTFBS',
        'HumanEnhancer':       'HumanEnhancer',
        'RNAedit':             'RNAedit',
        'PolyPhen2':           'PolyPhen2',
        'SIFT':                'SIFT',
        'LSSNP':               'LS-SNP',
        'UniProt':             'UniProt',
        'EqtlMethMetabStudy':  'EqtlMethMetabStudy'
    }

    def __repr__(self):
        """Display information about the table."""
        return "{} ({}) <{}:{} pheno: {} study: {}".format(
            self.id, self.snpid, self.chrom, self.pos, self.phenotype_desc,
            self.study.title
        )

    def __int__(self):
        """Return ID number."""
        return self.id

    def __str__(self):
        """Return coordinates."""
        return "{}:{}".format(self.chrom, self.pos)


class Study(Base):

    """To store study information."""

    __tablename__ = "studies"

    id               = Column(Integer, primary_key=True, index=True)
    pmid             = Column(String(100), index=True)
    title            = Column(String, index=True)
    journal          = Column(String)
    author           = Column(String)
    grasp_ver        = Column(Integer, index=True)
    noresults        = Column(Boolean)
    results          = Column(Integer)
    qtl              = Column(Boolean)
    snps             = relationship("SNP",
                                    back_populates='study')
    phenotype_id     = Column(Integer, ForeignKey('phenos.id'),
                              index=True)
    phenotype        = relationship("Phenotype",
                                    back_populates="studies")
    phenotype_cats   = relationship("PhenoCats",
                                    secondary=study_pheno_assoc,
                                    back_populates="studies")
    datepub          = Column(Date)
    in_nhgri         = Column(Boolean)
    locations        = Column(String)
    mf               = Column(Boolean)
    mf_only          = Column(Boolean)
    platforms        = relationship("Platform",
                                    secondary=study_plat_assoc,
                                    back_populates="studies")
    snp_count        = Column(String)
    imputed          = Column(Boolean)
    population_id    = Column(Integer, ForeignKey('populations.id'))
    population       = relationship("Population",
                                    backref="studies")
    total            = Column(Integer)
    total_disc       = Column(Integer)
    disc_pops        = Column(Integer, index=True)  # Will hold a bitwise flag
    european         = Column(Integer)
    african          = Column(Integer)
    east_asian       = Column(Integer)
    south_asian      = Column(Integer)
    hispanic         = Column(Integer)
    native           = Column(Integer)
    micronesian      = Column(Integer)
    arab             = Column(Integer)
    mixed            = Column(Integer)
    unspecified       = Column(Integer)
    filipino         = Column(Integer)
    indonesian       = Column(Integer)
    total_rep        = Column(Integer)
    rep_pops         = Column(Integer, index=True)  # Will hold a bitwise flag
    rep_european     = Column(Integer)
    rep_african      = Column(Integer)
    rep_east_asian   = Column(Integer)
    rep_south_asian  = Column(Integer)
    rep_hispanic     = Column(Integer)
    rep_native       = Column(Integer)
    rep_micronesian  = Column(Integer)
    rep_arab         = Column(Integer)
    rep_mixed        = Column(Integer)
    rep_unspecified  = Column(Integer)
    rep_filipino     = Column(Integer)
    rep_indonesian   = Column(Integer)
    sample_size      = Column(String)  # Maybe parse this better
    replication_size = Column(String)  # Maybe parse this better

    columns = {
        'id':               'ID',
        'pmid':             'PubmedID',
        'title':            'Study',
        'author':           '1st_author',
        'journal':          'Journal',
        'grasp_ver':        'GRASPversion?',
        'noresults':        'No results flag',
        'results':          '#results',
        'qtl':              'IsEqtl/meQTL/pQTL/gQTL/Metabolmics?',
        'snps':             'Link to all SNPs in this study',
        'phenotypes':       'Phenotype categories assigned',
        'datepub':          'DatePub',
        'in_nhgri':         'In NHGRI GWAS catalog (8/26/14)?',
        'locations':        'Specific place(s) mentioned for samples',
        'mf':               'Includes male/female only analyses in discovery and/or replication?',
        'mf_only':          'Exclusively male or female study?',
        'platforms':        'Platform [SNPs passing QC]',
        'snp_count':        'From "Platform [SNPs passing QC]"',
        'imputed':          'From "Platform [SNPs passing QC]"',
        'population_id':    'Primary key of population table',
        'population':       'GWAS description, link to table',
        'total':            'Total Discovery + Replication sample size',
        'total_disc':       'Total discovery samples',
        'disc_pops':        'A bitwise flag that shows presence/absence of discovery populations',
        'european':         'European',
        'african':          'African ancestry',
        'east_asian':       'East Asian',
        'south_asian':      'Indian/South Asian',
        'hispanic':         'Hispanic',
        'native':           'Native',
        'micronesian':      'Micronesian',
        'arab':             'Arab/ME',
        'mixed':            'Mixed',
        'unpecified':       'Unspec',
        'filipino':         'Filipino',
        'indonesian':       'Indonesian',
        'total_rep':        'Total replication samples',
        'rep_pops':         'A bitwise flag that shows presence/absence of replication populations',
        'rep_european':     'European.1',
        'rep_african':      'African ancestry.1',
        'rep_east_asian':   'East Asian.1',
        'rep_south_asian':  'Indian/South Asian.1',
        'rep_hispanic':     'Hispanic.1',
        'rep_native':       'Native.1',
        'rep_micronesian':  'Micronesian.1',
        'rep_arab':         'Arab/ME.1',
        'rep_mixed':        'Mixed.1',
        'rep_unpecified':   'Unspec.1',
        'rep_filipino':     'Filipino.1',
        'rep_indonesian':   'Indonesian.1',
        'sample_size':      'Initial Sample Size, string description of integer population counts above.',
        'replication_size': 'Replication Sample Size, string description of integer population counts above.',
    }

    @property
    def population_information(self):
        """Display a summary of population data."""
        outstr = ["Primary population: {}\n".format(self.population.population),
                  "Individuals: {}\n".format(self.total),
                  "Discovery populations: {}; Total: {}\n".format(
                      self.disc_pops.to_simple_str, self.total_disc
                  )]
        for pop in ['european', 'african', 'east_asian',
                    'south_asian', 'hispanic', 'native',
                    'micronesian', 'arab', 'unspecified',
                    'filipino', 'indonesian']:
            outstr.append('\t{}: {}\n'.format(pop, eval('self.' + pop)))

        outstr.append("Replication populations: {}; Total: {}\n".format(
            self.rep_pops.to_simple_str, self.total_rep
        ))
        for pop in ['european', 'african', 'east_asian',
                    'south_asian', 'hispanic', 'native',
                    'micronesian', 'arab', 'unspecified',
                    'filipino', 'indonesian']:
            outstr.append('\t{}: {}\n'.format(pop, eval('self.rep_' + pop)))

    def __repr__(self):
        """Display informaertn about this study."""
        return "{} <{}:{} {} ({}; Disc Pops: {}; Rep Pops: {})>".format(
            self.id, self.author, self.journal, self.title,
            self.phenotype_desc, self.disc_pops.to_simple_str,
            self.rep_pops.to_simple_str)

    def __str__(self):
        """Display refertnce."""
        return "{}: {} ({})\nSNPS: {}\nInds: {}\n".format(
            self.journal, self.title, self.author, self.snp_count, self.total,
        ) + "Disc Pops: {}; Rep Pops: {}; EUR: {}; AFR: {}".format(
            self.disc_pops.to_simple_str, self.rep_pops.to_simple_str,
            self.european, self.african
        )

    def __int__(self):
        """Return ID number."""
        return self.id

    def __len__(self):
        """Return total individual count."""
        return int(self.total)


class Phenotype(Base):

    """To store the primary phenotype."""

    __tablename__ = "phenos"

    id        = Column(Integer, primary_key=True,
                       index=True)
    phenotype = Column(String, index=True, unique=True)
    alias     = Column(String, index=True)
    studies   = relationship("Study",
                             back_populates="phenotype")

    def __repr__(self):
        """Display information."""
        return "{} <{} (alias: {})>".format(self.id, self.phenotype,
                                     self.alias)

    def __int__(self):
        """Return ID number."""
        return self.id

    def __str__(self):
        """Display phenotype name."""
        return "{}".format(self.phenotype)


class PhenoCats(Base):

    """To store the lists of phenotype categories."""

    __tablename__ = "pheno_cats"

    id       = Column(Integer, primary_key=True,
                      index=True)
    category = Column(String, index=True, unique=True)
    alias    = Column(String, index=True)
    snps     = relationship("SNP",
                            secondary=snp_pheno_assoc,
                            back_populates="phenotype_cats")
    studies  = relationship("Study",
                            secondary=study_pheno_assoc,
                            back_populates="phenotype_cats")

    def __repr__(self):
        """Display information."""
        return "{} <{} (alias: {})>".format(self.id, self.category,
                                     self.alias)

    def __int__(self):
        """Return ID number."""
        return self.id

    def __str__(self):
        """Display phenotype name."""
        return "{}".format(self.category)


class Platform(Base):

    """To store the platform information."""

    __tablename__ = "platforms"

    id       = Column(Integer, primary_key=True,
                      index=True)
    platform = Column(String, index=True, unique=True)
    studies  = relationship("Study",
                            secondary=study_plat_assoc,
                            back_populates="platforms")

    def __init__(self, platform):
        """Create self."""
        self.platform = platform

    def __repr__(self):
        """Display information."""
        return "{} <{}>".format(self.id, self.platform)

    def __int__(self):
        """Return ID number."""
        return self.id

    def __str__(self):
        """Display platform name."""
        return "{}".format(self.platform)


class Population(Base):

    """To store the platform information."""

    __tablename__ = "populations"

    id         = Column(Integer, primary_key=True,
                        index=True)
    population = Column(String, index=True, unique=True)

    def __init__(self, population):
        """Create self."""
        self.population = population

    def __repr__(self):
        """Display information."""
        return "{} <{}>".format(self.id, self.population)

    def __int__(self):
        """Return ID number."""
        return self.id

    def __str__(self):
        """Display platform name."""
        return "{}".format(self.population)

