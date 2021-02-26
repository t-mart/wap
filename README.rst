wap (WoW Addon Packager)
========================

.. teaser-begin

.. image:: https://github.com/t-mart/wap/actions/workflows/ci.yml/badge.svg?branch=master
   :target: https://github.com/t-mart/wap/actions/workflows/ci.yml
   :alt: GitHub Actions status for master branch

.. image:: https://codecov.io/gh/t-mart/wap/branch/master/graph/badge.svg?token=AVOA4QWTBL
   :target: https://codecov.io/gh/t-mart/wap
   :alt: Code Coverage on codecov.io

.. image:: https://img.shields.io/pypi/v/wow-addon-packager
   :target: https://pypi.org/project/wow-addon-packager/
   :alt: Latest release on PyPI

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code styled with black

.. image:: https://img.shields.io/github/license/t-mart/wap
   :target: https://github.com/t-mart/wap/blob/master/LICENSE
   :alt: MIT licensed

.. image:: https://readthedocs.org/projects/wow-addon-packager/badge/?version=latest
   :target: https://wow-addon-packager.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status


``wap`` is a user-friendly World of Warcraft addon packager.

.. image:: https://raw.githubusercontent.com/t-mart/wap/master/docs/demo.gif
   :alt: wap demo

Features
--------

- Builds and uploads your addons to CurseForge
- Creates retail or classic WoW addons, or both!
- Installs your addons to your Addons folder for fast development feedback
- Generates valid TOC files automagically
- Sets up new addon projects quickly, ready to go with one command
- Consolidates all configuration in one easy-to-edit file
- Supports Windows, macOS, and Linux

.. teaser-end

Getting started
---------------

1. `Download <https://www.python.org/downloads/>`_ and install Python 3.9 or greater.

2. Install ``wap`` with pip:

   .. code-block:: console

      $ pip install -U wow-addon-packager

3. Create a new project:

   .. code-block:: console

      $ wap quickstart MyAddon  # or whatever name you'd like!

  and answer the prompted questions. Don't worry too much about your answers -- you can
  always change them later in your configuration file.

4. Build your addon

   .. code-block:: console

      $ wap build

5. Test your addon out in your local WoW installation:

   .. code-block:: console

      # Windows
      $ wap dev-install --wow-addons-path "C:\Program Files (x86)\World of Warcraft\_retail_\Interface\AddOns"

      # macOS
      $ wap dev-install --wow-addons-path "/Applications/World of Warcraft/_retail_/Interface/AddOns"

6. Upload your project to CurseForge

   .. code-block:: console

      $ wap upload --addon-version "dev" --curseforge-token "<your-token>"

   You can generate a new token at `<https://authors.curseforge.com/account/api-tokens>`_.

Further Help
------------

See the official documentation site. There's a lot more information there!

Also, the ``wap`` command is fully documented in its help text. View it with:

.. code-block:: console

   $ wap --help
   $ wap build --help
   $ wap upload --help
   # ... etc

Contributing
------------

See `CONTRIBUTING.rst <docs/CONTRIBUTING.rst>`_.

TODOs
-----

- localization via curseforge?
- Dockerfile
- Dockerfile github action `<https://docs.github.com/en/actions/creating-actions/creating-a-docker-container-action>`_
