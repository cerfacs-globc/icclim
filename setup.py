#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

MINIMAL_REQUIREMENTS = [
    # todo: Unpin numpy 1.22 once numba works with it (numba comes with xclim)
    #       https://github.com/numba/numba/issues/7754
    "numpy>=1.16,<1.22",
    "xarray>=0.17",
    "xclim>=0.34",
    "cftime>=1.4.1",
    "dask[array]",
    "netCDF4>=1.5.7",
    "pyyaml",
    "psutil",
    "zarr",
    "rechunker>=0.3, !=0.4",
    "fsspec",
]

setup(
    name="icclim",
    version="5.2.1",
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
