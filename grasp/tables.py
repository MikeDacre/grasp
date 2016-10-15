"""
Table descriptions in SQLAlchemy ORM.

       Created: 2016-10-08
 Last modified: 2016-10-14 19:16

"""
# Database Table Descriptors
from sqlalchemy import Table      as _Table
from sqlalchemy import Column     as _Column
from sqlalchemy import Index      as _Index
from sqlalchemy import ForeignKey as _ForeignKey
from sqlalchemy import BigInteger as _BigInteger
from sqlalchemy import Integer    as _Integer
from sqlalchemy import String     as _String
from sqlalchemy import Float      as _Float
from sqlalchemy import Date       as _Date
from sqlalchemy import Boolean    as _Boolean

from sqlalchemy.orm             import relationship     as _relationship
from sqlalchemy.ext.declarative import declarative_base as _declarative_base

# Flags
from .ref import PopFlag as _PopFlag

# MyVariant functions
import myvariant

__all__ = ["SNP", "Phenotype", "PhenoCats", "Platform", "Population"]

Base = _declarative_base()

###############################################################################
#                             Association Tables                              #
###############################################################################

snp_pheno_assoc = _Table(
    'snp_pheno_association', Base.metadata,
    _Column('snp_id', _BigInteger, _ForeignKey('snps.id')),
    _Column('pheno_id', _Integer, _ForeignKey('pheno_cats.id'))
)

study_pheno_assoc = _Table(
    'study_pheno_association', Base.metadata,
    _Column('study_id', _Integer, _ForeignKey('studies.id')),
    _Column('pheno_id', _Integer, _ForeignKey('pheno_cats.id'))
)

study_plat_assoc = _Table(
    'study_platform_association', Base.metadata,
    _Column('study_id', _Integer, _ForeignKey('studies.id')),
    _Column('platform_id', _Integer, _ForeignKey('platforms.id'))
)

###############################################################################
#                               Database Tables                               #
###############################################################################


class SNP(Base):

    """An SQLAlchemy Talble for GRASP SNPs"""

    __tablename__ = "snps"

    id                 = _Column(_BigInteger, primary_key=True, index=True)
    snpid              = _Column(_String, index=True)
    chrom              = _Column(_String(10), index=True)
    pos                = _Column(_Integer, index=True)
    pval               = _Column(_Float, index=True)
    NHLBIkey           = _Column(_String, index=True)
    HUPfield           = _Column(_String)
    LastCurationDate   = _Column(_Date)
    CreationDate       = _Column(_Date)
    population_id      = _Column(_Integer, _ForeignKey('populations.id'))
    population         = _relationship("Population",
                                      backref="snps")
    study_id           = _Column(_Integer, _ForeignKey('studies.id'))
    study              = _relationship("Study",
                                      back_populates="snps")
    study_snpid        = _Column(_String)
    paper_loc          = _Column(_String)
    phenotype_desc     = _Column(_String, index=True)
    phenotype_cats     = _relationship("PhenoCats",
                                      secondary=snp_pheno_assoc,
                                      back_populates="snps")
    InGene             = _Column(_String)
    NearestGene        = _Column(_String)
    InLincRNA          = _Column(_String)
    InMiRNA            = _Column(_String)
    InMiRNABS          = _Column(_String)
    dbSNPfxn           = _Column(_String)
    dbSNPMAF           = _Column(_String)
    dbSNPinfo          = _Column(_String)
    dbSNPvalidation    = _Column(_String)
    dbSNPClinStatus    = _Column(_String)
    ORegAnno           = _Column(_String)
    ConservPredTFBS    = _Column(_String)
    HumanEnhancer      = _Column(_String)
    RNAedit            = _Column(_String)
    PolyPhen2          = _Column(_String)
    SIFT               = _Column(_String)
    LSSNP              = _Column(_String)
    UniProt            = _Column(_String)
    EqtlMethMetabStudy = _Column(_String)

    _Index('chrom_pos', 'chrom', 'pos')

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

    @property
    def snp_loc(self):
        """Return a simple string containing the SNP location."""
        return "{}:{}".format(self.chrom, self.pos)

    @property
    def hvgs_ids(self):
        """Get the HVGS ID from myvariant"""
        if not hasattr(self, '_hvgs_ids'):
            mv = myvariant.MyVariantInfo()
            q = mv.query(self.snp_loc, fields='id', as_dataframe=True)
            self._hvgs_ids = q['hits'].tolist()
        return self._hvgs_ids

    def get_variant_info(self, fields="dbsnp", pandas=True):
        """Use the myvariant API to get info about this SNP.

        Note that this service can be very slow.
        It will be faster to query multiple SNPs.

        :fields: Choose fields to display from:
                 docs.myvariant.info/en/latest/doc/data.html#available-fields
                 Good choices are 'dbsnp', 'clinvar', or 'gwassnps'
                 Can also use 'grasp' to get a different version of this info.
        :pandas: Return a dataframe instead of dictionary.
        """
        mv = myvariant.MyVariantInfo()
        return mv.getvariants(self.hvgs_ids, fields=fields,
                              as_dataframe=pandas, df_index=True)

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

    id               = _Column(_Integer, primary_key=True, index=True)
    pmid             = _Column(_String(100), index=True)
    title            = _Column(_String, index=True)
    journal          = _Column(_String)
    author           = _Column(_String)
    grasp_ver        = _Column(_Integer, index=True)
    noresults        = _Column(_Boolean)
    results          = _Column(_Integer)
    qtl              = _Column(_Boolean)
    snps             = _relationship("SNP",
                                    back_populates='study')
    phenotype_id     = _Column(_Integer, _ForeignKey('phenos.id'),
                              index=True)
    phenotype        = _relationship("Phenotype",
                                    back_populates="studies")
    phenotype_cats   = _relationship("PhenoCats",
                                    secondary=study_pheno_assoc,
                                    back_populates="studies")
    datepub          = _Column(_Date)
    in_nhgri         = _Column(_Boolean)
    locations        = _Column(_String)
    mf               = _Column(_Boolean)
    mf_only          = _Column(_Boolean)
    platforms        = _relationship("Platform",
                                    secondary=study_plat_assoc,
                                    back_populates="studies")
    snp_count        = _Column(_String)
    imputed          = _Column(_Boolean)
    population_id    = _Column(_Integer, _ForeignKey('populations.id'))
    population       = _relationship("Population",
                                    backref="studies")
    total            = _Column(_Integer)
    total_disc       = _Column(_Integer)
    disc_pop_flag    = _Column(_Integer, index=True)  # Will hold a bitwise flag
    european         = _Column(_Integer)
    african          = _Column(_Integer)
    east_asian       = _Column(_Integer)
    south_asian      = _Column(_Integer)
    hispanic         = _Column(_Integer)
    native           = _Column(_Integer)
    micronesian      = _Column(_Integer)
    arab             = _Column(_Integer)
    mixed            = _Column(_Integer)
    unspecified      = _Column(_Integer)
    filipino         = _Column(_Integer)
    indonesian       = _Column(_Integer)
    total_rep        = _Column(_Integer)
    rep_pop_flag     = _Column(_Integer, index=True)  # Will hold a bitwise flag
    rep_european     = _Column(_Integer)
    rep_african      = _Column(_Integer)
    rep_east_asian   = _Column(_Integer)
    rep_south_asian  = _Column(_Integer)
    rep_hispanic     = _Column(_Integer)
    rep_native       = _Column(_Integer)
    rep_micronesian  = _Column(_Integer)
    rep_arab         = _Column(_Integer)
    rep_mixed        = _Column(_Integer)
    rep_unspecified  = _Column(_Integer)
    rep_filipino     = _Column(_Integer)
    rep_indonesian   = _Column(_Integer)
    sample_size      = _Column(_String)  # Maybe parse this better
    replication_size = _Column(_String)  # Maybe parse this better

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
    def disc_pops(self):
        """Convert disc_pop_flag to PopFlag."""
        return _PopFlag(self.disc_pop_flag)

    @property
    def rep_pops(self):
        """Convert rep_pop_flag to PopFlag."""
        return _PopFlag(self.rep_pop_flag)

    @property
    def population_information(self):
        """Display a summary of population data."""
        outstr = ["Primary population: {}\n".format(self.population.population),
                  "Individuals: {}\n".format(self.total),
                  "Discovery populations: {}; Total: {}\n".format(
                      self.disc_pops.to_simple_str(), self.total_disc
                  )]
        for pop in ['european', 'african', 'east_asian',
                    'south_asian', 'hispanic', 'native',
                    'micronesian', 'arab', 'unspecified',
                    'filipino', 'indonesian']:
            outstr.append('\t{}: {}\n'.format(pop, eval('self.' + pop)))

        outstr.append("Replication populations: {}; Total: {}\n".format(
            self.rep_pops.to_simple_str(), self.total_rep
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
            self.phenotype.phenotype, self.disc_pops.to_simple_str(),
            self.rep_pops.to_simple_str())

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

    id        = _Column(_Integer, primary_key=True,
                       index=True)
    phenotype = _Column(_String, index=True, unique=True)
    alias     = _Column(_String, index=True)
    studies   = _relationship("Study",
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

    id       = _Column(_Integer, primary_key=True,
                      index=True)
    category = _Column(_String, index=True, unique=True)
    alias    = _Column(_String, index=True)
    snps     = _relationship("SNP",
                            secondary=snp_pheno_assoc,
                            back_populates="phenotype_cats")
    studies  = _relationship("Study",
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

    id       = _Column(_Integer, primary_key=True,
                      index=True)
    platform = _Column(_String, index=True, unique=True)
    studies  = _relationship("Study",
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

    id         = _Column(_Integer, primary_key=True,
                        index=True)
    population = _Column(_String, index=True, unique=True)

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

