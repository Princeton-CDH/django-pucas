import os
import sys
from setuptools import find_packages, setup
from pucas import __version__

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

REQUIREMENTS = ['django>=1.8', 'django-cas-ng>=3.6', 'ldap3']
TEST_REQUIREMENTS = ['pytest', 'pytest-django', 'pytest-cov']
if sys.version_info < (3, 0):
    TEST_REQUIREMENTS.append('mock')


setup(
    name='pucas',
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    license='Apache License, Version 2.0',
    description='Django app to login with CAS and populate user accounts with LDAP.',
    long_description=README,
    url='https://github.com/Princeton-CDH/django-pucas',
    install_requires=REQUIREMENTS,
    setup_requires=['pytest-runner'],
    tests_require=TEST_REQUIREMENTS,
    extras_require={
        'test': TEST_REQUIREMENTS,
    },
    author='CDH @ Princeton',
    author_email='digitalhumanities@princeton.edu',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: System :: Systems Administration :: Authentication/Directory',
        'Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP',
    ],
)
