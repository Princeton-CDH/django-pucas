import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-pucas',
    version='0.5',
    packages=find_packages(),
    include_package_data=True,
    license='Apache ',
    description='Django app to login with CAS and populate user accounts with LDAP.',
    long_description=README,
    # GitHub URL todo
    url='',
    install_requires=['django-cas-ng', 'ldap3'],
    author='CDH @ Princeton',
    author_email='digitalhumanities@princeton.edu',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.10',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # TODO: update these
        'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.4', ?
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: System :: Systems Administration :: Authentication/Directory',
        'Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP',
    ],
)
