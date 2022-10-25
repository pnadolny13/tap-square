#!/usr/bin/env python
from setuptools import setup

setup(
    name="tap-square",
    version="0.1.0",
    description="Singer.io tap for extracting data",
    author="Stitch",
    url="http://singer.io",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["tap-square"],
    install_requires=[
        "singer-python==5.9.0",
        "requests==2.20.0", 
        "genson==1.1.0", 'pandas'
    ],
    entry_points="""
    [console_scripts]
    tap-square=tap_square:main
    """,
    packages=["tap-square"],
    package_data={
        "schemas": ["tap-square/schemas/*.json"]
    },
    include_package_data=True,
)
