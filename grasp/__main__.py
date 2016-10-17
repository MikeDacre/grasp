"""
A Simple GRASP (grasp.nhlbi.nih.gov) API based on SQLAlchemy and Pandas

============   ======================================
Author         Michael D Dacre <mike.dacre@gmail.com>
Organization   Stanford University
License        MIT License, use as you wish
Created        2016-10-08
Version        0.3.0b1
============   ======================================

 Last modified: 2016-10-17 00:18

This is the front-end to a python grasp api, intended to allow easy database
creation and simple querying.  For most of the functions of this module, you
will need to call the module directly.
"""
import os
import sys
import argparse
from textwrap import dedent

import pandas as pd

from grasp import db
from grasp import info
from grasp import query
from grasp import config
from grasp import tables as t

from grasp.ref import PHENO_CATS, PHENOS, POPS, FLAGS, TABLE_INFO


def command_line_parser():
    """Parse command line options.

    Returns:
        argparse parser
    """

    parser  = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    subparsers = parser.add_subparsers(dest='modes',
                                       metavar='{search,conf,info,init}')

    # Search database
    search_info = dedent(
        """\
        Query for SNPs in the database.
        By default returns a tab-delimeted list of SNPs with the following\
        columns:
            'id', 'snpid', 'study_snpid', 'chrom', 'pos', 'phenotype', 'pval'

        The --extra flag adds these columns:
            'InGene', 'InMiRNA', 'inLincRNa', 'LSSNP'

        The --study-info flag adds these columns:
            'study_id (PMID)', 'title'

        The --db-snp flag uses the myvariant API to pull additional data
        from db_snp.
        """
    )
    search = subparsers.add_parser('search', aliases=['s', 'lookup'],
                                   description=search_info,
                                   help="Query database for variants by " +
                                   "location or id")
    search.add_argument('query', help="rsID, chrom:loc or chrom:start-end")
    search.add_argument('--extra', action='store_true',
                        help="Add some extra columns to output")
    search.add_argument('--study-info', action='store_true',
                        help="Include study title and PMID")
    search.add_argument('--db-snp', action='store_true',
                        help="Add dbSNP info to output")
    search.add_argument('--pandas', action='store_true',
                        help="Write output as a pandas dataframe")
    search.add_argument('-o', '--out', dest='search_outfile', metavar='',
                        help='File to write to, default STDOUT.')
    search.add_argument('--path', dest='search_path', metavar='',
                        default='.', help="PATH to write files to")

    # Manage config
    conf = subparsers.add_parser('conf', aliases=['config'],
                                 help="Manage local config")
    cgrp = conf.add_mutually_exclusive_group()
    cgrp.add_argument('--db', dest='cdb', metavar=None,
                      choices=['sqlite', 'postgresql', 'mysql'],
                      help="Set the current database platform.")
    cgrp.add_argument('--get-path', dest='cdpath', action='store_true',
                      help="Change the sqlite file path")
    cgrp.add_argument('--set-path', dest='cpath', metavar='PATH',
                      help="Change the sqlite file path")
    cgrp.add_argument('--init', dest='cinit', action='store_true',
                      help="Initialize the config with default settings. " +
                      "Will ERASE your old config!")

    # Print column info
    dinfo_info = dedent(
        """\
        Write data summaries (also found on the wiki) to a file or the\
        console.

        Choices:
            all:                  Will write everything to separate rst files,
                                  ignores all other flags except `--path`
            phenotypes:           All primary phenotypes.
            phenotype_categories: All phenotype categories.
            populations:          All primary populations.
            population_flags:     All population flags.
            snp_columns:          All SNP columns.
            study_columns:        All Study columns.
        """)
    dinfo = subparsers.add_parser('info', help="Display database info",
                                  description=dinfo_info)
    dinfo.add_argument('display',
                       choices={'phenotypes', 'phenotype_categories',
                                'populations', 'population_flags',
                                'snp_columns', 'study_columns',
                                'all'},
                       help="Choice of item to display, if all, results " +
                       "are written to independant rst files, and optional " +
                       "args are ignored")
    dinfo.add_argument('-o', '--out', dest='info_outfile', metavar='',
                       help='File to write to, default STDOUT.')
    dinfo.add_argument('--path', dest='info_path', metavar='',
                       default='.', help="PATH to write files to")
    # Not implemented yet
    # dinfo.add_argument('--write-as', choices={'table', 'tab', 'list'},
    #                    default='table', help="How to write the output.")

    # Initialize the database
    init = subparsers.add_parser('init', help="Initialize the database")
    init.add_argument('study_file',
                      help="GRASP study file from: " +
                      "github.com/MikeDacre/grasp/blob/master/grasp2_studies.txt")
    init.add_argument('grasp_file',
                      help="GRASP tab delimeted file")
    init.add_argument('-n', '--no-progress', action='store_false',
                      help="Do not display a progress bar")

    return parser


def main(argv=None):
    """Parse command line options to run as a script."""
    if not argv:
        argv = sys.argv[1:]

    parser = command_line_parser()

    args = parser.parse_args(argv)

    if args.modes == 'init':
        print("This will overwrite your existing database.")
        ans = input("Are you sure? [y/N] ")
        if not ans.lower() == 'y':
            return
        print("Initializing")
        db.initialize_database(args.study_file, args.grasp_file,
                               progress=args.no_progress)

    elif args.modes == 'search':
        if args.pandas and not args.search_outfile:
            print('Must include outfile if requesting pandas')
            return 1

        outcols  = [t.SNP.study_snpid, t.SNP.snpid, t.SNP.NHLBIkey,
                    t.SNP.chrom, t.SNP.pos, t.SNP.phenotype_desc,
                    t.SNP.pval]
        if args.extra:
            outcols += [t.SNP.InGene, t.SNP.InMiRNA, t.SNP.InLincRNA,
                        t.SNP.LSSNP]
        if args.study_info:
            outcols += [t.Study.pmid, t.Study.title]
            study = True
        else:
            study = False

        if args.query.startswith('rs'):
            snps = query.lookup_rsid(args.query, study=study,
                                     columns=outcols, pandas=True)
        else:
            chrom, pos = args.query.split(':')
            snps = query.lookup_location(chrom, pos, study=study,
                                         columns=outcols, pandas=True)

        if args.db_snp:
            mv = query.get_variant_info(snps)
            snps = pd.concat([snps, mv], axis=1)

        snps.index.name = 'rsID'

        # Write output
        out = os.path.join(args.search_path, args.search_outfile) \
            if args.search_outfile else sys.stdout
        if args.pandas:
            snps.to_pickle(out)
        else:
            with db._open_zipped(out, 'w') as fout:
                snps.to_csv(fout, sep='\t')

    elif args.modes == 'info':
        if args.display == 'all':
            with open(os.path.join(args.info_path, 'table_columns.rst'),
                      'w') as fout:
                fout.write(TABLE_INFO.format(
                    study=info.display_study_columns(),
                    snp=info.display_snp_columns()
                ))
            with open(os.path.join(args.info_path, 'pheno_cats.rst'),
                      'w') as fout:
                fout.write(PHENO_CATS.format(
                    info.get_phenotype_categories(table=True)
                ))
            with open(os.path.join(args.info_path, 'phenos.rst'),
                      'w') as fout:
                fout.write(PHENOS.format(
                    info.get_phenotypes(table=True)
                ))
            with open(os.path.join(args.info_path, 'pops.rst'),
                      'w') as fout:
                fout.write(POPS.format(
                    info.get_populations(table=True)
                ))
            with open(os.path.join(args.info_path, 'pop_flags.rst'),
                      'w') as fout:
                fout.write(POPS.format(
                    info.get_population_flags(table=True)
                ))
        else:
            out = os.path.join(args.info_path, args.info_outfile) \
                if args.info_outfile else sys.stdout
            command = 'display' if args.display == 'study' \
                or args.display == 'snp' else 'get'
            with db._open_zipped(out, 'w') as fout:
                fout.write(eval('info.{}_{}(table=True)'.format(command,
                                                                args.display)))

    elif args.modes == 'config':
        if args.cdb:
            if not os.path.exists(config.CONFIG_FILE):
                print('Config does not exist, you must create it first.',
                      'Initializing config creation...')
                config.init_config_interactive()
            config.config['DEFAULT']['DatabaseType'] = args.cdb
            config.write_config()

        elif args.cinit:
            config.init_config_interactive()

        elif args.cdpath:
            print("{}".format(config.CONFIG_FILE))

        elif args.cpath:
            if not os.path.isfile(args.cpath):
                print("{} Does not exist.".format(args.cpath))
                ans = input('Use anyway? [y/N] ')
                if not ans == 'y':
                    return
            config.config['sqlite']['DatabaseFile'] = os.path.abspath(
                args.cpath
            )
            config.write_config()

        else:
            parser.conf.print_help()
    else:
        parser.print_help()

if __name__ == '__main__':
    sys.exit(main())
