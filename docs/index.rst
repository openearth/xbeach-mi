.. XBeachMI documentation master file, created by
   sphinx-quickstart on Fri Jul 24 12:14:33 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to XBeachMI's documentation!
====================================

XBeach MI (Multiple Instances) is a Python wrapper for XBeach that
allows the user to run multiple instances of XBeach
simultaneously. Each instance can have its own settings. Possible
applications are:

#. Running XBeach in stationairy and instationairy mode alternating depending on the wave conditions

#. Running XBeach with multiple wind conditions and averaging the result (MORMERGE)

The XBeach MI Python wrapper is BMI compatible.
   
Contents:

.. toctree::
   :maxdepth: 2

   example
   sourcecode

Command-line tools
------------------

The XBeach MI wrapper can be executed from the command-line using the
"xbeach-mi" command.  See for more information the *--help* option.

xbeach-mi
^^^^^^^^^

.. automodule:: xbeachmi.cmd
                :members:


Source code repository
----------------------

The XBeach MI source code can be downloaded from the OpenEarth GitHub
repository: `<https://github.com/openearth/xbeach-mi/>`_.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

