|bin-restauth-import|
=====================

.. only:: man

   Synopsis
   --------

   | |bin-restauth-import-bold| [**-h**] [**--gen-passwords**] [**--overwrite-passwords**]
   |      [**--overwrite-properties**] [**--skip-existing-users**]
   |      [**--skip-existing-groups**] [**--using** *ALIAS*] [*file*]

   Description
   -----------

|bin-restauth-import-as-cmd| can be used to import data into RestAuth using a
specially formatted JSON file.  Please see |restauth-import-format| for a
description of how exactly the data must be formatted.

.. only:: homepage

   .. _dist-specific-bin-restauth-import:

   Name of |bin-restauth-import|
   -----------------------------

   If you :doc:`installed from source </install/from-source>`, the script is
   installed as :command:`restauth-import.py`. If you installed RestAuth via
   your distributions package management system, the script is usually called
   :command:`restauth-import`.

Usage
-----

.. only:: html

   .. include:: gen/restauth-import-usage.rst

|bin-restauth-import-as-cmd| by default imports the data as is and does not
overwrite any already existing data. Various options allow you to configure if
specific kinds input data should take precedence over whats already in the
RestAuth database.

If you don't specifiy *file*, |bin-restauth-import-as-cmd| reads from standard
input.

Examples
--------

.. example:: |bin-restauth-import-bold| *import.json*

   Simply import the data in the file *import.json*. If data already exists in
   the local service, it will be ignored. This means:

   * passwords will only be used if the user didn't exist before.
   * properties that already exist will be ignored.
   * group memberships are added.

.. example:: |bin-restauth-import-bold| **--gen-passwords** *import.json*

   Import data and generate new passwords for *new* users (or services) that
   don't have a password in the input data.

.. example:: |bin-restauth-import-bold| **--overwrite-passwords** **--overwrite-properties** *import.json*

   Import data and overwrite passwords of already existing users. Also set
   properties that already exist to the new value found in the input data.

.. example:: |bin-restauth-import-bold| **--skip-existing-users** **--skip-existing-groups** *import.json*

   Skip users or groups that already exist alltogether. Properties won't be used
   even if they weren't set before, memberships to groups are not added if the
   group previously existed.

Available parameters
--------------------

.. include:: gen/restauth-import-parameters.rst

Influential environment variables
---------------------------------

.. include:: includes/env-variables.rst

.. only:: man

   See Also
   ^^^^^^^^

   The input data format used by this script: :manpage:`restauth-import(5)`

   Other scripts: :manpage:`restauth-service(1)`, :manpage:`restauth-user(1)`, :manpage:`restauth-group(1)`
