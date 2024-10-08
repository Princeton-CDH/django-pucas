CHANGELOG
=========

0.9.1
-----

* Update GitHub Actions for publishing releases to PyPI

0.9
---

* Update installation instructions to use current django url syntax
* Update sample login template to use correct django admin `extrastyle` block
* Update styles and wording for PU CAS login include template

0.8
---
* Now tested against Django 3.2-4.2
* Add testing for Python 3.9-3.11
* Using GitHub Actions for continuous integration

0.7
----
* Drop support for Python 2.7
* No longer tested against Django 1.8-1.10; now tested against 3.0 and 3.1
* Add testing for Python 3.8
* Default branch name for current release is now **main**

0.6
-----
* Add support for multiple fallbacks on LDAP attributes. See `PR #3 <https://github.com/Princeton-CDH/django-pucas/pull/>`_.
* Improve handling for missing LDAP attributes.
* Now requires django-cas-ng 3.6 or greater.
* Document tested Django and Python versions.

0.5.2
-----

* Document permissions in the README.

0.5.1
-----

* Now available via pip install from pypi!
* Minor unit test updates to improve coverage.

0.5 Django-Pucas
----------------

Initial release of Django plugin for CAS authentication with local Princeton University setup
in mind. Features below are provided in the form of user stories.

Developer
~~~~~~~~~
* As a developer, I want to be able to install pucas as a Django plugin from the git repo for easy install.
* As a developer, I want to be able to use pucas as a drop in replacement for CAS/LDAP authentication for easy authentication.
* As a developer, I want to have example templates for installations available in the pucas source code.
* As a developer, I want the option to ask for addition information from the LDAP server as part of user initialization.

Admin User
~~~~~~~~~~
* As an admin user, I want to be a able to add users using manage.py commands and automatically add their LDAP info, including creating super users, for easy management.
* As an admin user, I want to be able to see who has been added as CAS users.
* As an admin user, I want to still be able to create a user with Django's build in authentication so that I can add users not in my organization's LDAP.

User
~~~~
* As a user, I want to be able authenticate easily using Princeton (or another configurable) CAS SSO solution.
* As a user, I want to be able to use the usual Django sign-in process with only one referral to the outside CAS service.
