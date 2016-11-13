#!/usr/bin/env python
import os

from setuptools import setup

ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

with open(os.path.join(SOURCE_DIR, 'requirements.txt'), 'r') as f:
    requirements = f.read().splitlines()

setup(
    name="docker-image-py",
    version='0.1.1',
    description="Parse docker image as distribution does.",
    url='https://github.com/realityone/docker-image-py',
    packages=['docker_image'],
    install_requires=requirements,
    zip_safe=False,
)
