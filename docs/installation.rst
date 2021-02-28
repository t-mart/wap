Installation
============

#. `Download Python 3.9 or greater`_. Python is the programming language on which ``wap`` runs.

   Afterwards, ensure you have an acceptable version:

   .. code-block:: console

     $ python --version
     Python 3.9.1

#. Install ``wap`` using ``pip``, the Python package installer, that comes with Python.

   .. code-block:: console

     $ pip install --upgrade --user wow-addon-packager

   .. note::
      You can also use this command to upgrade ``wap`` from a previous version if you have
      already installed it.

   Advanced Python users should consider installing ``wap`` into a virtual
   environment. I really like `pipx`_ for global commands like this that need
   isolation.

#. Ensure you can run ``wap``:

   .. code-block:: console

     $ wap --version
     wap, version 0.6.0

   The exact version in the output may be different.

#. You're done! Go ahead and start running some :ref:`commands <commands>`.

.. _`Download Python 3.9 or greater`: https://www.python.org/downloads/
.. _`pipx`: https://github.com/pipxproject/pipx