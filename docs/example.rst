Example
=======

In order to run XBeach MI you need a compiled XBeach library with BMI
interface (bmi branch or trunk rev >= 4748) that is in your path. Next
you need a regular XBeach model setup including params.txt file. The
params.txt file may contain Mako templating syntax to make it instance
dependent. Last but not least you need a separate XBeach MI
configuration file that configures the transitions from one instance
to another and the combined output of XBeach MI to a netCDF file.

You can find an example configuration in the GIT repository
`<https://github.com/openearth/xbeach-mi/tree/master/example>`_.
