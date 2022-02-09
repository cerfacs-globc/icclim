#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

from icclim import __version__

MINIMAL_REQUIREMENTS = [
    "numpy>=1.21,<1.22",  # todo unpin 1.22 once numba works with it
    "xarray>=0.19",
    "xclim>=0.33",
    "cftime>=1.5.0",
    "dask[array]>=2021.10.0",
    "netCDF4>=1.5.7",
    "pyyaml>=6.0",
]

setup(
    name="icclim",
    version=__version__,
    packages=find_packages(),
    author="Christian P.",
    author_email="christian.page@cerfacs.fr",
    description="Python library for climate indices calculation",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    include_package_data=True,
    url="https://github.com/cerfacs-globc/icclim",
    install_requires=MINIMAL_REQUIREMENTS,
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
    ],
)
