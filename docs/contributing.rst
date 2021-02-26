Contributing
============

Environment Setup
-----------------

1. Install `poetry <https://python-poetry.org/docs/#installation>`_. There are many
   installation methods, but you should **not** choose any that install poetry into the
   same virtualenv as wap itself -- packages of either may conflict with the packages
   of the other.
2. Within the repository, install the project dependencies:

   .. code-block:: console

      $ cd to/the/wap/repo
      $ poetry install


Linting
-------

New commits are checked to ensure style and consistency. You should run the following
command locally and ensure they return 0 exit codes. Otherwise, your commits will fail
the PR status checks.



.. code-block:: console

   $ poetry run mypy
   $ poetry run isort wap tests
   $ poetry run black wap tests

Additionally, if updating the README.rst, make sure to check twine too. The README.rst
is reused as the package ``long_description``, which is used on the PyPI page, and
therefore, must be valid:

.. code-block:: console

   $ poetry build
   $ poetry run twine check dist/*


Testing
-------

``wap`` uses ``pytest``. Run it (and generate a coverage report) with:

.. code-block:: console

   $ poetry run pytest tests --cov=wap --cov-report=xml

All new commits need to be 100% covered by tests. We use `Codecov`_ status checks to
enforce this. See `.coveragerc` for its configuration

Versioning
----------

``wap`` adheres to `Semantic Versioning <https://semver.org/>`_ for its releases. The
version will take the form ``x.y.z``. The commit from which the release is created will
be tagged with this version as its tag name.

To increment versions and propogate them around the repository for ``wap`` to use, we use
`bump2version <https://github.com/c4urself/bump2version>`_, which provides the
``bumpversion`` command. Its configuration file is located at ``.bumpversion.cfg``.

An important note is that between releases, the source code will contain the last
version released. This version number should be considered meaningless on unreleased
project states.

Release Process
---------------

1. A stopping point is identified in development to make a release. An inventory
   of changes on the master branch is performed and the appropriate next version is
   determined according to `SemVer rules <https://semver.org/#summary>`_.

2. On the master branch, this new version is incremented to with the ``bumpversion``.

   .. code-block:: console

      # replace <part> with one of "major", "minor", or "patch".
      $ bumpversion <part>

  This command:

  a. Increments the version in source code
  b. Creates a commit with this change
  c. Tags that commit with this new version as the tag name

3. The new commit and tag are pushed back to GitHub.

4. The CI workflow will run, and because the git ref is a tag, additional deploy
   steps will be taken, such as publishing to PyPI and creating a GitHub release
   asset.

.. _`Codecov`: https://about.codecov.io/