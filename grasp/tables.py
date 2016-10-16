"""
GRASP table descriptions in SQLAlchemy ORM.

These tables do not exist in the GRASP data, which is a single flat file. By
separating the data into these tables querying is much more efficient.

This submodule should only be used for querying.
"""
from collections import OrderedDict as _od

from tabulate import tabulate as _tb

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

# MyVariant functions
import myvariant

# Flags
from .ref import PopFlag as _PopFlag

__all__ = ["SNP", "Phenotype", "PhenoCats", "Platform", "Population"]

Base = _declarative_base()
"""The SQLAlchemy Base for the database."""

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

    """An SQLAlchemy Talble for GRASP SNPs.

    Study and phenotype information are pushed to other tables to minimize
    table size and make querying easier.

    Table Name:
        snps

    Columns:
        Described in the columns attribute

    Attributes:
        int:      The ID number of the SNP, usually the NHLBIkey
        str:      SNP loction expressed as 'chr:pos'
        hvgs_ids: A list of HGVS IDs for this SNP
        columns:  A dictionary of all columns 'column_name'=>('type', 'desc')
    """

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

    columns = _od([
        ('id',                 ('BigInteger',   'NHLBIkey') ),
        ('snpid',              ('String',       'SNPid') ),
        ('chrom',              ('String',       'chr') ),
        ('pos',                ('Integer',      'pos') ),
        ('pval',               ('Float',        'Pvalue') ),
        ('NHLBIkey',           ('String',       'NHLBIkey') ),
        ('HUPfield',           ('String',       'HUPfield') ),
        ('LastCurationDate',   ('Date',         'LastCurationDate') ),
        ('CreationDate',       ('Date',         'CreationDate') ),
        ('population_id',      ('Integer',      'Primary') ),
        ('population',         ('relationship', 'Link') ),
        ('study_id',           ('Integer',      'Primary') ),
        ('study',              ('relationship', 'Link') ),
        ('study_snpid',        ('String',       'SNPid') ),
        ('paper_loc',          ('String',       'LocationWithinPaper') ),
        ('phenotype_desc',     ('String',       'Phenotype') ),
        ('phenotype_cats',     ('relationship', 'Link') ),
        ('InGene',             ('String',       'InGene') ),
        ('NearestGene',        ('String',       'NearestGene') ),
        ('InLincRNA',          ('String',       'InLincRNA') ),
        ('InMiRNA',            ('String',       'InMiRNA') ),
        ('InMiRNABS',          ('String',       'InMiRNABS') ),
        ('dbSNPfxn',           ('String',       'dbSNPfxn') ),
        ('dbSNPMAF',           ('String',       'dbSNPMAF') ),
        ('dbSNPinfo',          ('String',       'dbSNPalleles') ),
        ('dbSNPvalidation',    ('String',       'dbSNPvalidation') ),
        ('dbSNPClinStatus',    ('String',       'dbSNPClinStatus') ),
        ('ORegAnno',           ('String',       'ORegAnno') ),
        ('ConservPredTFBS',    ('String',       'ConservPredTFBS') ),
        ('HumanEnhancer',      ('String',       'HumanEnhancer') ),
        ('RNAedit',            ('String',       'RNAedit') ),
        ('PolyPhen2',          ('String',       'PolyPhen2') ),
        ('SIFT',               ('String',       'SIFT') ),
        ('LSSNP',              ('String',       'LS') ),
        ('UniProt',            ('String',       'UniProt') ),
        ('EqtlMethMetabStudy', ('String',       'EqtlMethMetabStudy') ),
    ])
    """A description of all columns in this table."""

    @property
    def snp_loc(self):
        """Return a simple string containing the SNP location."""
        return "chr{}:{}".format(self.chrom, self.pos)

    @property
    def hvgs_ids(self):
        """The HVGS ID from myvariant."""
        if not hasattr(self, '_hvgs_ids'):
            mv = myvariant.MyVariantInfo()
            self._hvgs_ids = [i['_id'] for i in
                              mv.query(self.snp_loc, fields='id')['hits']]
        return self._hvgs_ids

    def get_variant_info(self, fields="dbsnp", pandas=True):
        """Use the myvariant API to get info about this SNP.

        Note that this service can be very slow.
        It will be faster to query multiple SNPs.

        Args:
            fields: Choose fields to display from:
                    `docs.myvariant.info/en/latest/doc/data.html#available-fields`_
                    Good choices are 'dbsnp', 'clinvar', or 'gwassnps'
                    Can also use 'grasp' to get a different version of this
                    info.
            pandas: Return a dataframe instead of dictionary.

        Returns:
            A dictionary or a dataframe.
        """
        mv = myvariant.MyVariantInfo()
        return mv.getvariants(self.hvgs_ids, fields=fields,
                              as_dataframe=pandas, df_index=True)

    def get_columns(self, return_as='list'):
        """Return all columns in the table nicely formatted.

        Display choices:
            list:       A python list of column names
            dictionary: A python dictionary of name=>desc
            long_dict:  A python dictionary of name=>(type, desc)

        Args:
            return_as:  {table,tab,list,dictionary,long_dict,id_dict}

        Returns:
            A list or dictionary
        """
        cols = self.columns
        if return_as == 'list':
            return [i[1] for i in cols.values()]
        elif return_as == 'dictionary':
            return {k: v[1] for k, v in cols.items()}
        elif return_as == 'long_dict':
            return cols
        else:
            raise Exception("'display_as' must be one of {table,tab,list}")

    def display_columns(self, display_as='table', write=False):
        """Return all columns in the table nicely formatted.

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
        cols = self.columns
        if display_as == 'table':
            out = _tb(
                [['Column', 'Description', 'Type']] +\
                [[k, v[1], v[0]] for k, v in cols.items()],
                headers='firstrow', tablefmt='grid'
            )
        elif display_as == 'tab':
            out = '\n'.join(
                ['\t'.join(['Column', 'Description', 'Type'])] +\
                ['\t'.join([k, v[1], v[0]]) for k, v in cols.items()],
            )
        elif display_as == 'list':
            out = '\n'.join([i[1] for i in cols.values()])
        else:
            raise Exception("'display_as' must be one of {table,tab,list}")
        if write:
            print(out)
        else:
            return out

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
        return self.snp_loc


class Study(Base):

    """An SQLAlchemy table to store study information.

    This table provides easy ways to query for SNPs by study information,
    including population and phenotype.

    Note: `disc_pop_flag` and `rep_pop_flag` are integer representations of
    a bitwise flag describing population, defined in ref.PopFlag. To see the
    string representation of this property, lookup `disc_pops` or `rep_pops`.

    Table Name:
        studies

    Columns:
        Described in the columns attribute.

    Attributes:
        int:       The integer ID number, usually the PMID, unless not indexed.
        str:       Summary data on this study.
        len:       The number of individuals in this study.
        disc_pops: A string displaying the number of discovery poplations.
        rep_pops:  A string displaying the number of replication poplations.
        columns:   A dictionary of all columns 'column_name'=>('type', 'desc')

        population_information:
            A multi-line string describing the populations in this study.

    """

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

    columns = _od([
        ('id',               ('Integer',      'id') ),
        ('pmid',             ('String',       'PubmedID') ),
        ('title',            ('String',       'Study') ),
        ('journal',          ('String',       'Journal') ),
        ('author',           ('String',       '1st_author') ),
        ('grasp_ver',        ('Integer',      'GRASPversion?') ),
        ('noresults',        ('Boolean',      'No results flag') ),
        ('results',          ('Integer',      '#results') ),
        ('qtl',              ('Boolean',      'IsEqtl/meQTL/pQTL/gQTL/Metabolmics?') ),
        ('snps',             ('relationship', 'Link to all SNPs in this study') ),
        ('phenotype_id',     ('Integer',      'ID of primary phenotype in Phenotype table') ),
        ('phenotype',        ('relationship', 'A link to the primary phenotype in the Phenotype table') ),
        ('phenotype_cats',   ('relationship', 'A link to all phenotype categories assigned in the PhenoCats table') ),
        ('datepub',          ('Date',         'DatePub') ),
        ('in_nhgri',         ('Boolean',      'In NHGRI GWAS catalog (8/26/14)?') ),
        ('locations',        ('String',       'Specific place(s) mentioned for samples') ),
        ('mf',               ('Boolean',      'Includes male/female only analyses in discovery and/or replication?') ),
        ('mf_only',          ('Boolean',      'Exclusively male or female study?') ),
        ('platforms',        ('relationship', 'Link to platforms in the Platform table. Platform [SNPs passing QC]') ),
        ('snp_count',        ('String',       'From "Platform [SNPs passing QC]"') ),
        ('imputed',          ('Boolean',      'From "Platform [SNPs passing QC]"') ),
        ('population_id',    ('Integer',      'Primary key of population table') ),
        ('population',       ('relationship', 'GWAS description, link to table') ),
        ('total',            ('Integer',      'Total Discovery + Replication sample size') ),
        ('total_disc',       ('Integer',      'Total discovery samples') ),
        ('disc_pop_flag',    ('Integer',      'A bitwise flag that shows presence/absence of discovery populations') ),
        ('european',         ('Integer',      'European') ),
        ('african',          ('Integer',      'African ancestry') ),
        ('east_asian',       ('Integer',      'East Asian') ),
        ('south_asian',      ('Integer',      'Indian/South Asian') ),
        ('hispanic',         ('Integer',      'Hispanic') ),
        ('native',           ('Integer',      'Native') ),
        ('micronesian',      ('Integer',      'Micronesian') ),
        ('arab',             ('Integer',      'Arab/ME') ),
        ('mixed',            ('Integer',      'Mixed') ),
        ('unpecified',       ('Integer',      'Unspec') ),
        ('filipino',         ('Integer',      'Filipino') ),
        ('indonesian',       ('Integer',      'Indonesian') ),
        ('total_rep',        ('Integer',      'Total replication samples') ),
        ('rep_pop_flag',     ('Integer',      'A bitwise flag that shows presence/absence of replication populations') ),
        ('rep_european',     ('Integer',      'European.1') ),
        ('rep_african',      ('Integer',      'African ancestry.1') ),
        ('rep_east_asian',   ('Integer',      'East Asian.1') ),
        ('rep_south_asian',  ('Integer',      'Indian/South Asian.1') ),
        ('rep_hispanic',     ('Integer',      'Hispanic.1') ),
        ('rep_native',       ('Integer',      'Native.1') ),
        ('rep_micronesian',  ('Integer',      'Micronesian.1') ),
        ('rep_arab',         ('Integer',      'Arab/ME.1') ),
        ('rep_mixed',        ('Integer',      'Mixed.1') ),
        ('rep_unpecified',   ('Integer',      'Unspec.1') ),
        ('rep_filipino',     ('Integer',      'Filipino.1') ),
        ('rep_indonesian',   ('Integer',      'Indonesian.1') ),
        ('sample_size',      ('String',       'Initial Sample Size, string description of integer population counts above.') ),
        ('replication_size', ('String',       'Replication Sample Size, string description of integer population counts above.') ),
    ])
    """A description of all columns in this table."""

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

    def get_columns(self, return_as='list'):
        """Return all columns in the table nicely formatted.

        Display choices:
            list:       A python list of column names
            dictionary: A python dictionary of name=>desc
            long_dict:  A python dictionary of name=>(type, desc)

        Args:
            return_as:  {table,tab,list,dictionary,long_dict,id_dict}

        Returns:
            A list or dictionary
        """
        cols = self.columns
        if return_as == 'list':
            return [i[1] for i in cols.values()]
        elif return_as == 'dictionary':
            return {k: v[1] for k, v in cols.items()}
        elif return_as == 'long_dict':
            return cols
        else:
            raise Exception("'display_as' must be one of {table,tab,list}")

    def display_columns(self, display_as='table', write=False):
        """Return all columns in the table nicely formatted.

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
        cols = self.columns
        if display_as == 'table':
            out = _tb(
                [['Column', 'Description', 'Type']] +\
                [[k, v[1], v[0]] for k, v in cols.items()],
                headers='firstrow', tablefmt='grid'
            )
        elif display_as == 'tab':
            out = '\n'.join(
                ['\t'.join(['Column', 'Description', 'Type'])] +\
                ['\t'.join([k, v[1], v[0]]) for k, v in cols.items()],
            )
        elif display_as == 'list':
            out = '\n'.join([i[1] for i in cols.values()])
        else:
            raise Exception("'display_as' must be one of {table,tab,list}")
        if write:
            print(out)
        else:
            return out

    def __repr__(self):
        """Display informaertn about this study."""
        return '{} <{}:{} "{}" ({}; Pop: {}Disc Pops: {}; Rep Pops: {})>'.\
            format(self.id, self.author, self.journal, self.title,
                   self.phenotype.phenotype, self.population.population,
                   self.disc_pops.to_simple_str(),
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

    """An SQLAlchemy table to store the primary phenotype.

    Table Name:
        phenos

    Columns:
        phenotype: The string phenotype from the GRASP DB, unique.
        alias:     A short representation of the phenotype, not unique.
        studies:   A link to the studies table.

    Attributes:
        int:  The ID number.
        str:  The name of the phenotype.
    """

    __tablename__ = "phenos"

    id        = _Column(_Integer, primary_key=True,
                        index=True)
    phenotype = _Column(_String, index=True, unique=True)
    alias     = _Column(_String, index=True)
    studies   = _relationship("Study",
                              back_populates="phenotype")

    def __repr__(self):
        """Display information."""
        return '{} <"{}" (alias: {})>'.format(self.id, self.phenotype,
                                              self.alias)

    def __int__(self):
        """Return ID number."""
        return self.id

    def __str__(self):
        """Display phenotype name."""
        return "{}".format(self.phenotype)


class PhenoCats(Base):

    """An SQLAlchemy table to store the lists of phenotype categories.

    Table Name:
        pheno_cats

    Columns:
        category: The category from the grasp database, unique.
        alias:    An easy to use alias of the category, not unique.
        snps:     A link to all SNPs in this category.
        studies:  A link to all studies in this category.

    Attributes:
        int: The PhenoCat ID
        str: The category name
    """

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
        return '{} <"{}" (alias: {})>'.format(self.id, self.category,
                                              self.alias)

    def __int__(self):
        """Return ID number."""
        return self.id

    def __str__(self):
        """Display phenotype name."""
        return "{}".format(self.category)


class Platform(Base):

    """An SQLAlchemy table to store the platform information.

    Table Name:
        platforms

    Columns:
        platform: The name of the platform from GRASP.
        studies:  A link to all studies using this platform.

    Attributes:
        int: The ID number of this platform
        str: The name of the platform
    """

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

    """An SQLAlchemy table to store the platform information.

    Table Name:
        populations

    Columns:
        population: The name of the population.
        studies:    A link to all studies in this population.
        snps:       A link to all SNPs in this populations.

    Attributes:
        int: Population ID number
        str: The name of the population
    """

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
