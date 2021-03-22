Contributing
============

First off, thank you for considering contributing to ``wap``!
It's people like *you* who make it such a great tool for everyone.

* No contribution is too small!
  Please submit as many fixes for typos and grammar bloopers as you can!
* Don't be afraid to open half-finished PRs, and ask questions if something is unclear!
* Try to limit each pull request to *one* change only.
* If your change is worth documenting to end users, add a section to the `changelog`_
  under "Unreleased".
* Since we squash on merge, it's up to you how you handle updates to the master branch.
  Whether you prefer to rebase on master or merge master into your branch, do whatever is more comfortable for you.
* *Always* add tests and docs for your code.
  This is a hard rule; patches with missing tests or documentation can't be merged.
* Make sure your changes pass the status checks.
  You won't get any feedback until it's green unless you ask for it.

Environment Setup
-----------------

#. Install `poetry <https://python-poetry.org/docs/#installation>`_. There are many
   installation methods, but you should **not** choose any that install poetry into the
   same virtualenv as wap itself -- packages of either may conflict with the packages
   of the other. (I like the pipx way, for example.)
#. Clone ``wap``

   .. code-block:: console

      $ git clone https://github.com/t-mart/wap.git
      $ cd wap

#. Within the repository, install the project dependencies:

   .. code-block:: console

      $ poetry install

   This will create a virtual environment for you automatically and install all the
   project dependencies into it.

Status Checks
-------------

New commits are statically analyzed in PR status checks to ensure style and proper
Python typing. PRs that fail status checks will not be merged.

The checks run are:

* ``isort`` to ensure ``import`` statements are sorted.
* ``black`` for consistent code styling.
* ``flake8`` for PEP8 compliance (and some other helpful things like unused imports).
* ``mypy`` for Python type checking throughout the code.
* ``twine`` to ensure the package can be uploaded to PyPI. This is mostly for
  the README.rst, which can contain errant syntax and break the publish of a release.

  .. note::

     We do not use ``twine`` for publishing. ``poetry`` does that, but does not have a
     "check" feature.

* ``pytest`` to ensure tests pass. The CI workflow will run tests on Windows, macOS and
  Linux (all of our supported platforms).

* `Codecov`_ for code coverage. All new commits need to be 100% covered by tests. See
  `.coveragerc` for its configuration.

* `Read the Docs`_ to ensure documentation can be built (no reStructuredText/Sphinx errors)

Running the checks locally
**************************

You can run a local version of these checks with:

.. code-block:: console

   $ make pre-commit
   or simply "make" because it is the default Makefile rule

While this ``make`` command is kept in sync with the CI workflow (as best we can), there
are some caveats:

* ``isort`` and ``black`` will actually update your code, instead of just
  checking for correctness. This is what you want.
* Locally, there is no way to easily check your commit's code coverage.

Documentation
-------------

All documentation is written in reStructuredText and lives in the ``docs/`` directory.
Once pushed, documentation will be build with ReadTheDocs.

You can start a helpful live-updating documentation server with:

.. code-block:: console

   $ make sphinx-autobuild

Then navigate to http://127.0.0.1:8000 to see the documentation as it will be built.

Versioning
----------

``wap`` adheres to `Semantic Versioning`_ for its releases. The
version will take the form ``x.y.z``. The commit from which the release is created will
be tagged with this version as its tag name.

To increment versions and propogate them around the repository for ``wap`` to use, we use
`bump2version`_, which provides the
``bumpversion`` command. Its configuration file is located at ``.bumpversion.cfg``.

An important note is that between releases, the source code will contain the last
version released. This version number should be considered meaningless on unreleased
project states.

Release Process
---------------

#. A stopping point is identified in development to make a release. An inventory
   of changes on the master branch is performed and the appropriate next version is
   determined according to `SemVer rules`_.

#. Move any items from the "Unreleased" section in the `changelog`_ to a new section
   for the release (or create the items if they do not exist). This section should be
   right under the "Unreleased" section.

   Additionally, update the URL for the "Unreleased" link at the bottom of the page. It
   should point to ``https://github.com/t-mart/wap/compare/v<new-version>...HEAD`` where
   ``<new-version>`` is the version that will be released.

#. On the master branch, this new version is incremented to with the ``bumpversion``.

   .. code-block:: console

      replace <part> with one of "major", "minor", or "patch".
      $ bumpversion <part>

   This command increments the version in source code, creates a commit with this change
   and indicative message, and finally tags that commit, using the new version as the
   tag name.

#. The new commit and tag are pushed to GitHub.

#. The `CI workflow`_ is triggered, and because the git ref is a tag, additional deploy
   steps will be taken, such as publishing to PyPI and creating a GitHub release
   asset.

.. _`Codecov`: https://about.codecov.io/
.. _`changelog`: https://github.com/t-mart/wap/CHANGELOG.rst
.. _`Read the Docs`: https://readthedocs.org/
.. _`CI workflow`: https://github.com/t-mart/wap/actions/workflows/ci.yml
.. _`Semantic Versioning`: https://semver.org/
.. _`SemVer rules`: https://semver.org/#summary
.. _`bump2version`: https://github.com/c4urself/bump2version
