Contributing
============

Versioning
----------

*wap* adheres to `Semantic Versioning <https://semver.org/>`_ for its releases. The
version will take the form ``x.y.z``. The commit from which the release is created will
be tagged with this version as its tag name.

To increment versions and propogate them around the repository for *wap* to use, we use
`bump2version <https://github.com/c4urself/bump2version>`_, which provides the
``bumpversion`` command. Its configuration file is located at ``.bumpversion.cfg``.

An important note is that between releases, the source code will contain the last
version released. Therefore, this version number is meaningless on unreleased project
states.

Release Process
---------------

1. A stopping point is identified in development to make a release. An inventory
   of changes on the master branch is performed and the appropriate next version is
   determined according to `SemVer rules <https://semver.org/#summary>`_.

2. On the master branch, this new version is incremented to with the ``bumpversion``.

   .. code-block:: sh

     # replace <part> with one of "major", "minor", or "patch".
     bumpversion <part>

  This command:

  a. Increments the version in source code
  b. Creates a commit with this change
  c. Tags that commit with this new version as the tag name

3. Any release-related actions are carried out, such as publishing to PyPI, creating a
   GitHub release, etc.

4. The commit and tag are pushed back to the repostiory on GitHub.

5. Development continues and the cycle starts again.
