.. _examples:

Examples
========

.. note:: In order to run XBeach MI you need a compiled XBeach library
          with BMI interface (bmi branch or trunk rev >= 4748) that is
          in your path.

.. note:: You can find the full examples described here in th GIT repository
          https://github.com/openearth/xbeach-mi/tree/master/example
          
For an XBeach MI run you need at least two files:

#. Regular ``params.txt`` file for XBeach

#. A XBeach MI JSON configuration file

In the following sections two example setups for XBeach MI are
explained. The first is a sequential run in which multiple XBeach
instances run in sequence (e.g. surfbeat for storm conditions and
stationary for average conditions). The second is a parallel run in
which multiple XBeach instances are run in parallel, while their
bathymetry is averaged (MORMERGE). It is possible to combine both
approaches in a single setup.
          
.. _sequential:

Sequential
----------

The XBeach MI configuration file describes the communication between
the different instances. It is in JSON format as shown below. Two
sections are particularly important for a sequential run: ``scenario``
and ``exchange``.

``scenario`` describes what instances should be activated at what
point in time. For a sequential run only one instance runs at a
time. Note that it is possible to provide a list of instances, which
would enable the parallel_ mode. Also note that all instances are
activated by default at the start of the simulation.

``exchange`` provides a list with all variables that are being
exchanged between instances in case the model switches from one
instance to another. For most sequential runs this list needs to
contain the majority of the XBeach output variable for the best
results as it ensures that the full model state is copied from one
instance to another.

.. literalinclude:: ../example/sequential/config.json
   :language: json
   :caption: config.json

Note that the XBeach MI configuration file references a single
``params.txt`` file through the ``params_file`` keyword. Consequently,
all instances share the same ``params.txt`` file and no differences
between the instances exist. Therefore, it is possible to add
templating makers to the ``params.txt`` file to make it instance
dependent. In the example below, the instance ``instat`` defines
surfbeat boundary conditions, while the instance ``stat`` defines
stationary boundary conditions. Please refer to the Mako templating
engine for all the possible templating options.

.. literalinclude:: ../example/sequential/params.txt
   :language: python
   :caption: params.txt

.. note:: Note that the grids of all instances should be equal, so it
          is not allowed to define different values for ``nx`` and
          ``ny`` between instances.

.. _parallel:

Parallel (MORMERGE)
-------------------

For a parallel run instances don't need to be defined by a scenario
(although it is possible), but can be defined by a simple list using
the ``instances`` keyword. The ``exchange`` list is generally much
smaller than for a sequential run and typically only holds the ``zb``
variable.

In addition, a keyword ``aggregate`` can be defined that specifies how
data from the different instances need to be aggregated. The
``method`` keyword defines the methodology or a reference to a custom
Python function. The ``options`` keyword holds key/value pairs that
are passed as options to the aggregation function. The ``interval``
defined the interval in seconds when the data between instances should
be aggregated and exchanged.

.. literalinclude:: ../example/parallel/config.json
   :language: json
   :caption: config.json

Also a parallel run uses a single ``params.txt`` file that uses Mako
templating differentiate between instances. In this example both
instances run in surfbeat mode, but with different boundary
conditions.
             
.. literalinclude:: ../example/parallel/params.txt
   :language: python
   :caption: params.txt

Nesting
-------

Not supported.
