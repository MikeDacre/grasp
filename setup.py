"""
Setup Script for Slurmy
"""
import os
import codecs

# Make setuptools work everywhere
import ez_setup
ez_setup.use_setuptools()

import setuptools
from setuptools import setup
log = setuptools.distutils.log

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with codecs.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Generate a list of python scripts
scpts = []
scpt_dir = os.listdir(os.path.join(here, 'bin'))
for scpt in scpt_dir:
    scpts.append(os.path.join('bin', scpt))

setup(
    name='grasp',
    version='0.1',
    description='A Simple GRASP (grasp.nhlbi.nih.gov) API based on SQLAlchemy and Pandas',
    long_description=long_description,
    url='https://github.com/MikeDacre/grasp',
    author='Michael Dacre',
    author_email='mike.dacre@gmail.com',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Environment :: Console',
        'Operating System :: Linux',
        'Natural Language :: English',
        'Topic :: Database',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='grasp sqlalchemy',

    requires=['sqlalchemy', 'pandas', 'tqdm'],
    install_requires=['python-dateutil'],  # Crashes if in requires.
    packages=['grasp'],
    scripts=scpts,
)
