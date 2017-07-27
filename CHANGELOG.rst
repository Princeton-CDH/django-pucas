CHANGELOG
=========

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