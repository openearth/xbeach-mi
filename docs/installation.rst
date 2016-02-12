Installation
============

This document describes the installation steps needed to get the
XBeach MI (Multiple Instances) framework to work on a Windows machine
(the screenshots may deviate slightly as they are from a Mac OS X
machine). If you have a working XBeach installation you can skip
step 1. If you have a working Python 2.7 installation with packages
numpy, netCDF4, multiprocessing and mako installed, you can skip
step 2.

1. Download XBeach
------------------

#. Go to http://xbeach.org.

.. figure:: images/image1.png
   
#. Choose ``Downloads`` and ``Releases and source``.
   
.. figure:: images/image2.png

#. Go to ``Daily builds`` and download ``XBeach rev. XXXX (with netCDF
   support)``. You need a recent version of XBeach (rev. >= 4748) that
   implements the Basic Model Interface (BMI).

.. figure:: images/image3.png
            
.. figure:: images/image4.png
   
2. Download Python
------------------

#. Google for ``Python XY`` (or ``Anaconda``).

.. figure:: images/image5.png
   
#. Follow the instructions to download Python XY (or Anaconda).

.. figure:: images/image6.png
   
#. Follow the instructions to install Python XY (or Anaconda). Do not
   forget to choose ``Full`` install and not the default installation
   configuration.

3. Download BMI and XBeach MI
-----------------------------

#. Go to http://github.com/openearth and search for ``bmi-python``.

.. figure:: images/image7.png
   
#. Choose ``Download ZIP``.

.. figure:: images/image8.png
   
#. Go back and search for ``xbeach-mi``.

.. figure:: images/image9.png
   
#. Choose ``Download ZIP``.

.. figure:: images/image10.png
 
4. Install BMI and XBeach MI
----------------------------

#. Unzip the downloaded ``bmi-python`` and ``xbeach-mi`` packages.

#. Go to the command line (Start > ``cmd``).

#. Go to the download directory of the ``bmi-python`` package.

#. Go to the directory that contains the ``setup.py`` file.

#. Run the command ``python setup.py install``.

.. figure:: images/image11.png

#. Go to the download directory of the ``xbeach-mi`` package that contains the ``setup.py`` file.
   
#. Again, run the command ``python setup.py install``.
 
5. Test XBeach MI
-----------------

#. Test the installation by running the command ``xbeach-mi --help``.

.. figure:: images/image12.png
   
#. Go to the ``example`` directory in the ``xbeach-mi`` download directory.
   
#. Run XBeach MI with the provided configuration file.

.. figure:: images/image13.png

#. Details on configuring and running XBeach MI can be found on the documentation website: examples_

