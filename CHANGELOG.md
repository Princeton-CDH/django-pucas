# Changelog

## 0.10.2

* Convert CHANGELOG from `.rst` to `.md`

## 0.10.1

* Correct version number

## 0.10

* Reorganize package under `/src` layout
* Switch from `setup.py` to `pyproject.toml` for package configuration
* Add `uv` support; update CI to use `uv sync` and `uv run pytest`
* Drop Python 3.9 support; now tested against Python 3.10–3.14
* Update publish workflow to use Python 3.12
* Convert README from `.rst` to `.md`
* Update license metadata to use SPDX expression (`Apache-2.0`)
* Suppress known deprecation warnings from `ldap3` 2.9.1 (upstream bug, expected fix in ldap3 2.10)

## 0.9.1

* Update GitHub Actions for publishing releases to PyPI

## 0.9

* Update installation instructions to use current django url syntax
* Update sample login template to use correct django admin `extrastyle` block
* Update styles and wording for PU CAS login include template

## 0.8

* Now tested against Django 3.2–4.2
* Add testing for Python 3.9–3.11
* Using GitHub Actions for continuous integration

## 0.7

* Drop support for Python 2.7
* No longer tested against Django 1.8–1.10; now tested against 3.0 and 3.1
* Add testing for Python 3.8
* Default branch name for current release is now **main**

## 0.6

* Add support for multiple fallbacks on LDAP attributes. See [PR #3](https://github.com/Princeton-CDH/django-pucas/pull/3).
* Improve handling for missing LDAP attributes.
* Now requires django-cas-ng 3.6 or greater.
* Document tested Django and Python versions.

## 0.5.2

* Document permissions in the README.

## 0.5.1

* Now available via pip install from PyPI.
* Minor unit test updates to improve coverage.

## 0.5 Django-Pucas

Initial release of Django plugin for CAS authentication with local Princeton University setup in mind.
