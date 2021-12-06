from setuptools import find_packages, setup, Extension


from icclim import __version__

module1 = Extension("libC", sources=["./icclim/libC.c"])

setup(
    name="icclim4",
    version=__version__,
    # TODO exclude tests files from find_packages
    packages=find_packages(),
    author="Christian P.",
    author_email="christian.page@cerfacs.fr",
    description="Python library for climate indices calculation",
    long_description=open("README.md").read(),
    include_package_data=True,
    ext_modules=[module1],
    url="https://github.com/cerfacs-globc/icclim",
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "License :: OSI Approved",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        "Topic :: Climate Index",
    ],
    # entry_points = {
    #    'console_scripts': [
    #        'proclame-sm = sm_lib.core:proclamer',
    #    ],
    # },
)
