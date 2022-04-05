#!/usr/bin/env python
# coding: utf-8
from setuptools import setup
# setup.cfg
setup(
    name='launchbase',
    packages=['launchbase'],
    entry_points={'console_scripts': ['launchbase=launchbase.__main__:main']},
    install_requires=[
        "prompt_toolkit>=3.0.0",
    ],
)
