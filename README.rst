django-pucas
============

**django-pucas** is a reusable `Django`_ application to simplify logging
into a Django application with CAS using `django-cas-ng`_.  Login and
creation of user accounts is handled by django-cas-ng; pucas adds
support for prepopulating user account data based on an LDAP search.

*pucas* should be pronounced like *pookas* for the Celtic spirit creature.

.. _Django: https://www.djangoproject.com/
.. _django-cas-ng: https://github.com/mingchen/django-cas-ng

Installation
------------

Use pip to install from GitHub::

    pip install git+https://github.com/Princeton-CDH/django-pucas.git#egg=pucas

Use ``@develop`` or ``@1.0`` to install a specific tagged release or
branch::

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
        'ATTRIBUTE_MAP': {
            'first_name': 'givenName',
            'last_name': 'sn',
            'email': 'mail'
        }
    }


Run migrations to create database tables required by django-cas-ng::

    python manage.py migrate

To make CAS login available on the Django admin login form, extend the
default admin login form and include or adapt the provided CAS login
template snippet.  An example admin login form is included at
``pucas/templates/pucas/sample-admin-login.html``; copy this to
``admin/login.html`` within a valid template directory and modify
as needed.

