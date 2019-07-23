django-pucas
============

.. image:: https://travis-ci.org/Princeton-CDH/django-pucas.svg?branch=master
   :target: https://travis-ci.org/Princeton-CDH/django-pucas
   :alt: Build status

.. image:: https://codecov.io/gh/Princeton-CDH/django-pucas/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/Princeton-CDH/django-pucas
  :alt: Code Coverage

.. image:: https://www.codefactor.io/repository/github/princeton-cdh/django-pucas/badge
   :target: https://www.codefactor.io/repository/github/princeton-cdh/django-pucas
   :alt: CodeFactor

.. image:: https://requires.io/github/Princeton-CDH/django-pucas/requirements.svg?branch=master
     :target: https://requires.io/github/Princeton-CDH/django-pucas/requirements/?branch=master
     :alt: Requirements Status

**django-pucas** is a reusable `Django`_ application to simplify logging
into a Django application with CAS using `django-cas-ng`_.  Login and
creation of user accounts is handled by django-cas-ng; pucas adds
support for prepopulating user account data based on an LDAP search.

*pucas* should be pronounced like *pookas* for the Celtic spirit creature.

.. _Django: https://www.djangoproject.com/
.. _django-cas-ng: https://github.com/mingchen/django-cas-ng

**django-pucas** is tested under:

* Django ``1.8-2.2``
* Python ``2.7, 3.5-3.7`` (excluding ``2.7`` for Django ``2+``)

**django-pucas** requires **django-cas-ng** 3.6 or greater.

Installation
------------

Use pip to install::

    pip install pucas

You can also install from Github.  Use ``@master`` or ``@0.5`` to install a
specific tagged release or branch (e.g., for the lastest code on ``develop``)::

    pip install git+https://github.com/Princeton-CDH/django-pucas.git@develop#egg=pucas

Configuration
-------------

Add both django-cas-ng and pucas to installed apps; enable authentication
middleware and django-cas-ng authentication backend::

    INSTALLED_APPS = (
        ...
        'django_cas_ng',
        'pucas',
        ...
    )

    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        ...
    )

    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'django_cas_ng.backends.CASBackend',
    )


Include the default django-cas-ng login and logout urls provided with pucas,
or configure them as needed based on the documentation::


    urlpatterns = [
        ...
        url(r'^accounts/', include('pucas.cas_urls')),
        ...
    ]

Add required configurations to ``settings.py``:

* **CAS_SERVER_URL** - Base URL of your CAS source

* Configure LDAP settings as needed to populate user attributes::

    PUCAS_LDAP = {
        'SERVERS': ['ldap1', 'ldap2'],
        'SEARCH_BASE': 'ou=users,dc=example,dc=com',
        'SEARCH_FILTER': "(uid=%(user)s)",
        # attributes to request from the LDAP server
        'ATTRIBUTES': ['givenName', 'sn', 'mail'],
        # mapping of User attributes to LDAP attributes
        # if passed list for the value, the first attribute to return a
        # value will be used
        'ATTRIBUTE_MAP': {
            'first_name': 'givenName',
            'last_name': 'sn',
            'email': ['mail', 'eduPersonPrincipalName']
        },
        # Optional local method to do additional user initialization
        # not handled by attribute map.  Method should take a user
        # object and ldap search result.
        'EXTRA_USER_INIT': 'myproj.myapp.models.init_profile_from_ldap'
        'BASE_DN': 'uid=username,o=your org,c=country_code',
        'BASE_PASSWORD': 'secreupasswordforyourldap',
    }

* Note: ``BASE_DN`` and ``BASE_PASSWORD`` are optional if you want
        to bind anonymously. Add them if they are required by your LDAP.
        This supports user/pass authentication.

Run migrations to create database tables required by django-cas-ng::

    python manage.py migrate

To make CAS login available on the Django admin login form, extend the
default admin login form and include or adapt the provided CAS login
template snippet.  An example admin login form is included at
``pucas/templates/pucas/sample-admin-login.html``; copy this to
``admin/login.html`` within a valid template directory and modify
as needed.

An example of a login template with local branding is provided at
``pucas/templates/pucas/sample-pu-login.html`` using re-usable template
snippets that can be adapted or re-used as appropriate.

For Django 1.8, you will need to override ``admin/login.html`` as a whole, as
extending the login template with itself causes a recursion error.

Usage
-----

Users can login with CAS and have a Django user account automatically
created and populated with LDAP data based on the settings.

Two manage commands are provided, for convenience.

* Use ``python manage.py ldapsearch netid1 netid2 netid3`` for testing
  your LDAP configuration and attributes.
* Use ``python manage.py createcasuser netid`` to initialize a new
  CAS account and populate data from LDAP without requiring the user
  to login first, as an aid to managing accounts and permissions.
  The optional flag ``--admin`` will give the new account superuser
  permissions

Development instructions
------------------------

This git repository uses git flow branching conventions.

Initial setup and installation:

- recommended: create and activate a python 3.5 virtualenv::

    virtualenv pucas -p python3.5
    source pucas/bin/activate

- pip install the package with its python dependencies::

    pip install -e .


Unit Testing
^^^^^^^^^^^^^

Unit tests are written with [py.test](http://doc.pytest.org/) but use some
Django test classes for compatibility with django test suites.  Running
the tests requires a minimal settings file for Django required configurations.

- Copy sample test settings and add a secret key::

    cp ci/testsettings.py.sample testsettings.py

- To run the tests, either use the configured setup.py test command::

    python setup.py test

- Or install test requirements and use py.test directly::

    pip install -e '.[test]'
    py.test


License
-------

**django-pucas** is distributed under the Apache 2.0 License.


©2016 Trustees of Princeton University.  Permission granted via
Princeton Docket #18-3398-1 for distribution online under a standard Open Source
license.  Ownership rights transferred to Rebecca Koeser provided software
is distributed online via open source.
