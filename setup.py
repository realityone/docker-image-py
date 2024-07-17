#!/usr/bin/env python
import os

from setuptools import setup

ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

install_requires = [
    'regex>=2019.4.14',
]

setup(
    name="docker-image-py",
    version='0.1.13',
    description="Parse docker image as distribution does.",
    url='https://github.com/realityone/docker-image-py',
    packages=['docker_image'],
    install_requires=install_requires,
    zip_safe=False,
)
