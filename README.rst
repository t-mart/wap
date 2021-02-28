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

|

``wap`` is a developer-friendly World of Warcraft addon packager.

.. image:: https://raw.githubusercontent.com/t-mart/wap/master/docs/_static/demo.gif
   :alt: wap demo

Features
--------

- Builds retail or classic WoW addons (or both!)
- Uploads your addons to CurseForge
- Installs your addons to your Addons folder for fast development feedback
- Generates valid TOC files automagically
- Sets up new addon projects quickly, ready to go with one command
- Consolidates all configuration in one easy-to-edit file
- Supports and is tested on Windows, macOS, and Linux
- Has awesome `documentation`_

.. _`documentation`: https://wow-addon-packager.readthedocs.io/en/stable

.. teaser-end


``wap`` in 5 minutes
--------------------

.. five-minutes-begin

This entire set of instructions is runnable without editing a single line of code!

1. `Download Python 3.9 or greater`_ and install it.

2. Install ``wap`` with pip:

   .. code-block:: console

      $ pip install --upgrade --user wow-addon-packager

3. Create a new project:

   .. code-block:: console

      $ wap quickstart MyAddon  # or whatever name you'd like!

   and answer the prompted questions. Don't worry too much about your answers -- you can
   always change them later in your configuration file.

   Then change to your new project's directory

   .. code-block:: console

      $ cd "MyAddon"

4. Build your addon

   .. code-block:: console

      $ wap build

5. Install your addon so you can test it out in your local WoW installation:

   Windows
      .. code-block:: console

         $ wap dev-install --wow-addons-path "C:\Program Files (x86)\World of Warcraft\_retail_\Interface\AddOns"

   macOS
      .. code-block:: console

         $ wap dev-install --wow-addons-path "/Applications/World of Warcraft/_retail_/Interface/AddOns"

6. Upload your project to CurseForge

   .. code-block:: console

      $ wap upload --addon-version "dev" --curseforge-token "<your-token>"

   You can generate a new token at Curseforge's `My API Tokens`_ page.

.. _`My API Tokens`: https://authors.curseforge.com/account/api-tokens
.. _`Download Python 3.9 or greater`: https://www.python.org/downloads/

.. five-minutes-end


Further Help
------------

See the `official documentation site`_. There's a lot more information there!

Also, the ``wap`` command is fully documented in its help text. View it with:

.. code-block:: console

   $ wap --help
   $ wap build --help
   $ wap upload --help
   ... etc

.. badge-begin

Badge
-----

If you'd like to show others in your documentation that you are using ``wap`` to package
your addon, you can include the following official badge (hosted by https://shields.io/):

.. image:: https://img.shields.io/badge/packaged%20by-wap-d33682
   :target: https://github.com/t-mart/wap
   :alt: Packaged by wap

Markdown
   .. code-block:: markdown

      [![Packaged by wap](https://img.shields.io/badge/packaged%20by-wap-d33682)](https://github.com/t-mart/wap)

reStructuredText
   .. code-block:: rst

      .. image:: https://img.shields.io/badge/packaged%20by-wap-d33682
         :target: https://github.com/t-mart/wap
         :alt: Packaged by wap

.. badge-end

Contributing
------------

See `how to contribute`_ in the official docs.

TODOs
-----

- localization via curseforge?
- Dockerfile github action `<https://docs.github.com/en/actions/creating-actions/creating-a-docker-container-action>`_

.. _`how to contribute`: https://wow-addon-packager.readthedocs.io/en/stable/contributing.html
.. _`official documentation site`: https://wow-addon-packager.readthedocs.io/en/stable

Copyright (c) 2021 Tim Martin
