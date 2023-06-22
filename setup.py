import os
import sys
from setuptools import find_packages, setup
from pucas import __version__

with open(os.path.join(os.path.dirname(__file__), "README.rst")) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

REQUIREMENTS = ["django>=1.8", "django-cas-ng>=3.6", "ldap3"]
TEST_REQUIREMENTS = ["pytest", "pytest-django", "pytest-cov"]
if sys.version_info < (3, 0):
    TEST_REQUIREMENTS.append("mock")


setup(
    name="pucas",
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    license="Apache License, Version 2.0",
    description="Django app to login with CAS and populate user accounts with LDAP.",
    long_description=README,
    url="https://github.com/Princeton-CDH/django-pucas",
    install_requires=REQUIREMENTS,
    setup_requires=["pytest-runner"],
    tests_require=TEST_REQUIREMENTS,
    extras_require={
        "test": TEST_REQUIREMENTS,
    },
    author="CDH @ Princeton",
    author_email="digitalhumanities@princeton.edu",
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: System :: Systems Administration :: Authentication/Directory",
        "Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP",
    ],
)
