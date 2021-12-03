#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

from icclim import __version__

MINIMAL_REQUIREMENTS = [
    "numpy>=1.16",
    "xarray>=0.17",
    "xclim>=0.31",
    "scipy>=1.2",
    "cftime>=1.4.1",
    "dask[array]>=2.6",
    "netCDF4>=1.5.7",
]

setup(
    name="icclim",
    version=__version__,
    # TODO exclude tests files from find_packages
    packages=find_packages(),
    author="Christian P.",
    author_email="christian.page@cerfacs.fr",
    description="Python library for climate indices calculation",
    long_description=open("README.md").read(),
    include_package_data=True,
    url="https://github.com/cerfacs-globc/icclim",
    install_requires=MINIMAL_REQUIREMENTS,
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
    ],
)
