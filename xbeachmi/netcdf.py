import netCDF4
from datetime import datetime


def initialize(ncfile, dimensions, variables=None, attributes=None, crs=None):
    '''Initialize netCDF4 file

    Creates an empty netCDF4 file with dimensions and variable
    containers according to a set of dictionaries for the dimensions,
    variables, global attributes and local coordinate reference system
    (crs). All dictionaries have the dimension/variable/attribute
    names as keys and values as values. Only the dictionary with
    variables does not contain values, since these are yet
    unknown. Instead this dictionary contains other dictionaries
    specifying at least the variables dimensions. For example:

    .. code-block:: json

       {
           "Ct" : {
               "dimensions" : ["y", "x", "fractions"]
           },
           "mass" : {
               "dimensions" : ["y", "x", "fractions", "layers"]
           },
           "zb" : {
               "dimensions" : ["y", "x"]
           }
        }

    Parameters
    ----------
    ncfile : str
        path to netCDF4 file
    dimensions : dict
        dict with dimension variables x, y, layers and fractions
    variables : dict
        dict of dicts with other variables, where each variable
        defines at least its dimensions
    attributes : dict
        dict with global netCDF attributes
    crs : dict
        dict with EPSG attributes for local coordinate reference system (crs)

    '''

    with netCDF4.Dataset(ncfile, 'w') as nc:

        ## add dimensions
        nc.createDimension('x', len(dimensions['x']))
        nc.createDimension('y', len(dimensions['y']))
        nc.createDimension('time', 0)
        nc.createDimension('nv', 2)
        nc.createDimension('nv2', 4)
        nc.createDimension('nv3', 128)
          
        ## add global attributes
        # see http://www.unidata.ucar.edu/software/thredds/current/netcdf-java/formats/DataDiscoveryAttConvention.html
        nc.Conventions = 'CF-1.6'
        nc.Metadata_Conventions = 'Unidata Dataset Discovery v1.0'
        nc.featureType = 'grid'
        nc.cdm_data_type = 'grid'
        nc.standard_name_vocabulary = 'CF-1.6'
        nc.title = ''
        nc.summary = ''
        nc.source = 'Windsurf'
        nc.id = ''
        nc.naming_authority = ''
        nc.time_coverage_start = ''
        nc.time_coverage_end = ''
        nc.time_coverage_resolution = ''
        nc.geospatial_lat_min = 0
        nc.geospatial_lat_max = 0
        nc.geospatial_lat_units = 'degrees_north'
        nc.geospatial_lat_resolution = ''
        nc.geospatial_lon_min = 0
        nc.geospatial_lon_max = 0
        nc.geospatial_lon_units = 'degrees_east'
        nc.geospatial_lon_resolution = ''
        nc.geospatial_vertical_min = 0
        nc.geospatial_vertical_max = 0
        nc.geospatial_vertical_units = ''
        nc.geospatial_vertical_resolution = ''
        nc.geospatial_vertical_positive = ''
        nc.institution = ''
        nc.creator_name = ''
        nc.creator_url = ''
        nc.creator_email = ''
        nc.project = ''
        nc.processing_level = ''
        nc.references = ''
        nc.keywords_vocabulary = 'NASA/GCMD Earth Science Keywords. Version 6.0'
        nc.keywords = ''
        nc.acknowledgment = ''
        nc.comment = ''
        nc.contributor_name = ''
        nc.contributor_role = ''
        nc.date_created = datetime.strftime(datetime.utcnow(), '%Y-%m-%dT%H:%MZ')
        nc.date_modified = datetime.strftime(datetime.utcnow(), '%Y-%m-%dT%H:%MZ')
        nc.date_issued = datetime.strftime(datetime.utcnow(), '%Y-%m-%dT%H:%MZ')
        nc.publisher_name = ''
        nc.publisher_email = ''
        nc.publisher_url = ''
        nc.history = ''
        nc.license = ''
        nc.metadata_link = '0'
        
        ## add variables
        nc.createVariable('x', 'float32', (u'x'))
        nc.variables['x'].long_name = 'x-coordinate'
        nc.variables['x'].standard_name = 'projection_x_coordinate'
        nc.variables['x'].units = 'm'
        nc.variables['x'].axis = 'X'
        nc.variables['x'].valid_min = 0
        nc.variables['x'].valid_max = 0
        nc.variables['x'].bounds = 'x_bounds'
        nc.variables['x'].grid_mapping = 'crs'
        nc.variables['x'].comment = ''
        
        nc.createVariable('y', 'float32', (u'y'))
        nc.variables['y'].long_name = 'y-coordinate'
        nc.variables['y'].standard_name = 'projection_y_coordinate'
        nc.variables['y'].units = 'm'
        nc.variables['y'].axis = 'Y'
        nc.variables['y'].valid_min = 0
        nc.variables['y'].valid_max = 0
        nc.variables['y'].bounds = 'y_bounds'
        nc.variables['y'].grid_mapping = 'crs'
        nc.variables['y'].comment = ''

        nc.createVariable('lat', 'float32', (u'y', u'x'))
        nc.variables['lat'].long_name = 'latitude'
        nc.variables['lat'].standard_name = 'latitude'
        nc.variables['lat'].units = 'degrees_north'
        nc.variables['lat'].valid_min = 0
        nc.variables['lat'].valid_max = 0
        nc.variables['lat'].bounds = 'lat_bounds'
        nc.variables['lat'].ancillary_variables = ''
        nc.variables['lat'].comment = ''
        
        nc.createVariable('lon', 'float32', (u'y', u'x'))
        nc.variables['lon'].long_name = 'longitude'
        nc.variables['lon'].standard_name = 'longitude'
        nc.variables['lon'].units = 'degrees_east'
        nc.variables['lon'].valid_min = 0
        nc.variables['lon'].valid_max = 0
        nc.variables['lon'].bounds = 'lon_bounds'
        nc.variables['lon'].ancillary_variables = ''
        nc.variables['lon'].comment = ''
        
        nc.createVariable('time', 'float64', (u'time',))
        nc.variables['time'].long_name = 'time'
        nc.variables['time'].standard_name = 'time'
        nc.variables['time'].units = 'seconds since 1970-01-01 00:00:00 0:00'
        nc.variables['time'].calendar = 'julian'
        nc.variables['time'].axis = 'T'
        nc.variables['time'].bounds = 'time_bounds'
        nc.variables['time'].ancillary_variables = ''
        nc.variables['time'].comment = ''
        
        nc.createVariable('instance', 'S1', (u'time', u'nv3'))
        nc.variables['instance'].long_name = 'instance'
        nc.variables['instance'].standard_name = ''
        nc.variables['instance'].units = ''
        nc.variables['instance'].valid_min = 0
        nc.variables['instance'].valid_max = 0
        nc.variables['instance'].ancillary_variables = ''
        nc.variables['instance'].comment = ''

        nc.createVariable('x_bounds', 'float32', (u'x', u'nv'))
        nc.variables['x_bounds'].units = 'm'
        nc.variables['x_bounds'].comment = 'x-coordinate values at the upper and lower bounds of each pixel.'
        
        nc.createVariable('y_bounds', 'float32', (u'y', u'nv'))
        nc.variables['y_bounds'].units = 'm'
        nc.variables['y_bounds'].comment = 'y-coordinate values at the left and right bounds of each pixel.'
        
        nc.createVariable('lat_bounds', 'float32', (u'y', u'x', u'nv2'))
        nc.variables['lat_bounds'].units = 'degrees_north'
        nc.variables['lat_bounds'].comment = 'latitude values at the north and south bounds of each pixel.'
        
        nc.createVariable('lon_bounds', 'float32', (u'y', u'x', u'nv2'))
        nc.variables['lon_bounds'].units = 'degrees_east'
        nc.variables['lon_bounds'].comment = 'longitude values at the west and east bounds of each pixel.'
        
        nc.createVariable('time_bounds', 'float32', (u'time', u'nv'))
        nc.variables['time_bounds'].units = 'seconds since 1970-01-01 00:00:00 0:00'
        nc.variables['time_bounds'].comment = 'time bounds for each time value'

        if variables is not None:
            for var, props in variables.iteritems():

                nc.createVariable(var, 'float32', props['dimensions'])
                nc.variables[var].long_name = var
                nc.variables[var].standard_name = ''
                nc.variables[var].units = ''
                nc.variables[var].scale_factor = 1.0
                nc.variables[var].add_offset = 0.0
                nc.variables[var].valid_min = 0
                nc.variables[var].valid_max = 0
                nc.variables[var].coordinates = ' '.join(props['dimensions'])
                nc.variables[var].grid_mapping = 'crs'
                nc.variables[var].source = ''
                nc.variables[var].references = ''
                nc.variables[var].cell_methods = ''
                nc.variables[var].ancillary_variables = ''
                nc.variables[var].comment = ''

        # set local coordinate system
        nc.createVariable('crs', 'int32', ())
        if crs is not None:
            for key, value in crs.iteritems():
                nc.variables['crs'] = set_ncattr(nc.variables['crs'], key, value)

        # set netcdf attributes
        if attributes is not None:
            for key, value in attributes.iteritems():
                nc = set_ncattr(nc, key, value)
            
        # store static data
        nc.variables['x'][:] = dimensions['x']
        nc.variables['y'][:] = dimensions['y']

        nc.variables['lat'][:,:] = 0.
        nc.variables['lon'][:,:] = 0.
        nc.variables['x_bounds'][:,:] = 0.
        nc.variables['y_bounds'][:,:] = 0.
        nc.variables['lat_bounds'][:,:] = 0.
        nc.variables['lon_bounds'][:,:] = 0.
        
#        # store model settings
#        grp = nc.createGroup('settings')
#        for k, v in self.params.iteritems():
#            if isinstance(v, bool):
#                grp.setncattr(k, int(v))
#            else:
#                grp.setncattr(k, v)


def append(ncfile, idx, variables):
    '''Append data to existing netCDF4 file

    Parameters
    ----------
    ncfile : str
        path to netCDF4 file
    idx : int
        time index to write to
    variables : dict
        dict with variable names (keys) and data to be
        appended (values)

    '''

    with netCDF4.Dataset(ncfile, 'a') as nc:
        nc.variables['time'][idx] = variables['time']
        for name, value in variables.iteritems():
            nc.variables[name][idx,...] = value
        nc.variables['time_bounds'][idx,0] \
            = 0 if idx == 0 else nc.variables['time'][idx]
        nc.variables['time_bounds'][idx,1] = variables['time']
    

def set_ncattr(nc, key, value):
    '''Set netCDF4 attribute safe for boolean values

    Parameters
    ----------
    nc : netCDF4.Dataset or netCDF4.Variable
        netCDF4 object to set attribute on
    key : str
        attribute name
    value : any
        attribute value

    Returns
    -------
    netCDF4.Dataset or netCDF4.Variable
        netCDF4 object with set attribute

    '''
    
    if isinstance(value, bool):
        nc.setncattr(key, int(value))
    else:
        nc.setncattr(key, value)

    return nc
