import os
import re
import json
import shutil
import logging
import numpy as np
from mako.template import Template
from bmi.wrapper import BMIWrapper
from bmi.api import IBmi
from multiprocessing import Process, Queue, JoinableQueue

import progress, netcdf, parsers


# initialize log
logger = logging.getLogger(__name__)


class XBeachMIWrapper:
    '''XBeachMI class

    Main class for XBeach MI model wrapper. XBeach MI is a wrapper for
    running multiple parallel instances of the XBeach model.

    '''

    
    def __init__(self, configfile=None):
        '''Initialize the class

        Parameters
        ----------
        configfile : str
            path to JSON configuration file, see
            :func:`~beachmi.model.XBeachMI.load_configfile`

        '''

        self.configfile = configfile


    def run(self):
        '''Start model time loop'''

        with XBeachMI(configfile=self.configfile) as self.engine:

            self.t = 0
            self.progress = progress.ProgressIndicator(
                duration=self.engine.get_end_time()
            )

            self.output_init()
            while self.t < self.progress.duration:
                self.progress.progress(self.t)
                self.engine.update()
                self.t = self.engine.get_current_time()
                self.output()


    def output_init(self):
        '''Initialize netCDF4 output file

        Creates an empty netCDF4 output file with the necessary
        dimensions, variables, attributes and coordinate reference
        system specification (crs).

        '''

        if self.engine.config.has_key('netcdf'):

            logger.debug('Initializing output...')
        
            cfg = self.engine.config['netcdf']

            # get dimension names for each variable
            variables = {
                v : { 'dimensions' : self.engine.get_dimensions(v) }
                for v in cfg['outputvars']
            }
        
            netcdf.initialize(cfg['outputfile'],
                              self.read_dimensions(),
                              variables=variables,
                              attributes=cfg['attributes'],
                              crs=cfg['crs'])

        self.iout = 0

        
    def output(self):
        '''Write model data to netCDF4 output file'''

        if self.engine.config.has_key('netcdf'):
            
            cfg = self.engine.config['netcdf']

            if self.progress.check_period(self.t, cfg['interval']):

                logger.debug('Writing output at t=%0.2f...' % self.t)
                
                # get dimension data for each variable
                variables = {v : self.engine.get_var(v) for v in cfg['outputvars']}
                variables['time'] = self.t
                variables['instance'] = self.engine.instance
        
                netcdf.append(cfg['outputfile'],
                              idx=self.iout,
                              variables=variables)

                self.iout += 1


    def read_dimensions(self):
        '''Read dimensions

        Parses individual model engine configuration files and read
        information regarding the dimensions of the composite domain,
        like the bathymetric grid, number of sediment fractions and
        number of bed layers.

        Returns
        -------
        dict
            dictionary with dimension variables

        '''

        dimensions = {}

        cfg_xbeach = parsers.XBeachParser(
            self.engine.instances[self.engine.instance]['configfile']).parse()

        # x and y
        if len(cfg_xbeach) > 0:
            dimensions['x'] = cfg_xbeach['xfile'].reshape(
                (cfg_xbeach['ny']+1,
                 cfg_xbeach['nx']+1))[0,:]
            dimensions['y'] = cfg_xbeach['yfile'].reshape(
                (cfg_xbeach['ny']+1,
                 cfg_xbeach['nx']+1))[:,0]
        else:
            dimensions['x'] = []
            dimensions['y'] = []

        # ensure lists
        for k, v in dimensions.iteritems():
            try:
                len(v)
            except:
                dimensions[k] = [v]
            
        return dimensions

                
class XBeachMI(IBmi):
    '''XBeach MI BMI compatible wrapper class

    A wrapper for a BMI compatible XBeach libarary to run multiple
    instances of an XBeach model simultaneously. The class spwans a
    new process for every model instance. A single model is updated at
    a time. If the running model instance is changed data between the
    previous and the next model instance is exchanged
    automatically. Optionally, both model instances are ran parallel
    for a certain transition time in which the upcoming model instance
    is updated with the bathymetry of the running model instance,
    while spinning up its own hydrodynamics.

    The wrapper takes its own JSON configuration file that describes
    what instances should be created and at what moments in the
    simulation the running instance should be changed. See for more
    information on the configuration
    :func:`~xbeach-mi.model.XBeachMI.load_configfile`.

    The params.txt file can be made instance dependent using the Mako
    templating system. See for more information on the templating
    options :func:`~xbeach-mi.model.XBeachMI.load_configfile`.

    The XBeach library should be compiled with Position Independent
    Compilation (-fPIC compiler flag) in order to support local memory
    storage.

    '''

    instance = None
    instances = {}
    transition = None
    next_index = 0

    dzmax = 0.05            # maximum bed level change per time step
    

    def __init__(self, configfile='', instance=None):
        '''Initialize class

        Parameters
        ----------
        configfile : str
            path to JSON configuration file, see
            :func:`~xbeach-mi.model.XBeachMI.load_configfile`
        instance : str
            initial running instance

        '''
        
        self.configfile = configfile
        self.instance = instance

        self.load_configfile()


    def load_configfile(self):
        '''Load JSON configuration file

        Loads JSON configuration file and create separate hidden model
        directories for each instance. The JSON configuration file may
        contain the following:

        .. literalinclude:: ../example/config.json
           :language: json

        The params.txt file may be instance dependent by using mako
        templating syntax. In the following example the instances
        "stat_morfac10" and "stat_morfac100" are both run with "instat
        = stat" and "morfac = 10" or "morfac = 100" respectively. Only
        the instance "instat" is run with "instat = jons" and no
        morfac.
        
        .. code-block:: text
        
           % if instance.startswith('stat_'):
           instat = stat
           % elif instance.startswith('instat_'):
           instat = jons
           % endif
           
           % if instance.endsiwth('_morfac10'):
           morfac = 10
           % elif instance.endsiwth('_morfac100'):
           morfac = 100
           % endif

        Apart from the variable "instance" also the variables "path",
        "parfile" and "tmplfile" can be used in the params.txt
        template. These variables refer to the absolute model
        execution path, the absolute path to the rendered params.txt
        file and the absolute path to the params.txt template file
        used.

        '''

        if os.path.exists(self.configfile):

            logger.debug('Reading configuration file "%s"...' % self.configfile)

            # store current working directory
            self.cwd = os.getcwd()

            # change working directry to location of configuration file
            if not os.path.isabs(self.configfile):
                self.configfile = os.path.abspath(self.configfile)
            fpath, fname = os.path.split(self.configfile)
            os.chdir(fpath)
            logger.debug('Changed directory to "%s"' % fpath)

            # load configuration file
            with open(fname, 'r') as fp:
                self.config = json.load(fp)
        else:
            raise IOError('Configuration file not found [%s]' % self.configfile)

        # read params.txt file
        if self.config.has_key('params_file'):
            if os.path.exists(self.config['params_file']):
                fpath, fname = os.path.split(self.config['params_file'])
                if not os.path.isabs(fpath):
                    fpath = os.path.join(os.getcwd(), fpath)

                # get instances
                instances = []
                if self.config.has_key('instances'):
                    instances.extend(self.config['instances'])
                if self.config.has_key('scenario'):
                    instances.extend([x[1] for x in self.config['scenario']])
                instances = np.unique(instances)
                
                # create a hidden model directory for each model
                # instance listed in the configuration file and copy
                # params.txt file and other model configuration files
                # to the model directory
                for instance in instances:

                    logger.debug('Creating working directory "%s"...' % instance)

                    # set initial running instance
                    if not self.instance:
                        self.instance = instance

                    # create instance variables
                    self.instances[instance] = {'process': None,
                                                'queue_to': JoinableQueue(),
                                                'queue_from': Queue(),
                                                'configfile': '',
                                                'markers': {}}

                    # create hidden model directory
                    subdir = '.%s' % instance
                    if os.path.exists(subdir):
                        shutil.rmtree(subdir)
                    shutil.copytree(fpath, subdir,
                                    ignore=lambda src, files: [f
                                                               for f in files
                                                               if f.startswith('.') or 
                                                               f.endswith('.nc') or
                                                               f.endswith('.log')])

                    # create backup of original params.txt file
                    parfile = os.path.join(subdir, fname)
                    tmplfile = os.path.join(subdir, '%s.tmpl' % fname)
                    shutil.copyfile(parfile, tmplfile)

                    # store instance-specific mako template markers
                    self.instances[instance]['markers'] = {
                        'instance':instance,
                        'path':os.path.abspath(subdir),
                        'parfile':os.path.abspath(parfile),
                        'tmplfile':os.path.abspath(tmplfile)
                    }

                    self.instances[instance]['configfile'] = os.path.abspath(parfile)

                # render templates
                for instance in self.instances.itervalues():

                    # set global mako template markers
                    markers = instance['markers']
                    markers['instances'] = self.instances.keys()

                    logger.debug('Rendering template "%s"...' % markers['tmplfile'])
                    
                    template = Template(filename=markers['tmplfile'])
                    with open(markers['parfile'], 'w') as fp:
                        rendered = template.render(**markers)
                        fp.write('defuse = 0\n') # disable time explosion checks
                        fp.write(rendered)


    def update_instance(self):
        '''Change instance if needed according to scenario

        Change instance according to scenario and initiates transition
        period just before instance change.

        '''

        if self.config.has_key('scenario'):
            if self.next_index < len(self.config['scenario']):
                logger.debug('Update instance...')
                t = self.get_current_time()
                tc, instance = self.config['scenario'][self.next_index]
                if t >= tc:
                    self.set_instance(instance)
                    self.next_index += 1
                

    def set_instance(self, instance):
        '''Change instance, set time and exchange data

        Parameters
        ----------
        instance : str
            name of next running instance

        '''

        if instance in self.instances.keys():
            if instance != self.instance:
                logger.info('Start transition from running instance to "%s"...' % instance)
                self.transition = {
                    'time': self._call('get_current_time'),
                    'vars': {
                        'zb': self._call('get_var', ('zb',))
                    }
                }
                self.sync_time(instance)
                self.exchange_data(instance, incremental=False)
                self.instance = instance
        else:
            raise ValueError('Invalid instance [%s]' % instance)
            

    def sync_time(self, instance):
        '''Synchronize time between current and next running instance

        Parameters
        ----------
        instance : str
            name of next running instance

        '''

        logger.debug('Synchronizing time...')
        
        t1 = self._call('get_current_time') - self.config['transition_time']
        t2 = self._call('get_current_time', instance=instance)
        self._call('update', (t2 - t1,), instance=instance)
        

    def exchange_data(self, instance, incremental=True):
        '''Exchange data between current and next running instance

        Parameters
        ----------
        instance : str
            name of next running instance
        incremental : bool
            switch to maximize bed level change

        '''

        for var in self.config['exchange']:
            logger.debug('Exchanging "%s"...' % var)
            val = self._call('get_var', (var,))
            self._call('set_var', (var, val), instance=instance)

#        zb = self._call('get_var', ('zb',))
#            
#        zb0 = self._call('get_var', ('zb',), instance=instance)
#        hh = self._call('get_var', ('hh',), instance=instance)
#        wetz = self._call('get_var', ('wetz',), instance=instance)
#    
#        if incremental:
#            dz = zb - zb0
#            dz[dz >  self.dzmax] =  self.dzmax
#            dz[dz < -self.dzmax] = -self.dzmax
#            zb = zb0 + dz
#    
#        if np.any(np.abs(zb-zb0) > self.dzmax + 1e-4):
#            logger.warn('Maximum bed level change exceeded: %0.4f m' % np.max(np.abs(zb-zb0)))
#
#        zs = zb + hh * wetz
#            
#        self._call('set_var', ('zb', zb), instance=instance)
#        self._call('set_var', ('zs', zs), instance=instance)
            
            
    def start(self):
        '''Start all instance processes'''
        
        for name, instance in self.instances.iteritems():
            logger.debug('Starting instance "%s"...' % name)
            self.instances[name]['process'].start()
            
            
    def join(self):
        '''Wait for all instance processes to be finished'''
        
        for name, instance in self.instances.iteritems():
            logger.debug('Joining instance "%s"...' % name)
            self.instances[name]['process'].join()
            
            
    def run(self, parfile, queue_to, queue_from):
        '''Start instance process

        Parameters
        ----------
        parfile : str
            path to params.txt file for current instance
        queue_to : multiprocessing.JoinableQueue
            joinable queue for sharing data from master to subprocess
        queue_from : multiprocessing.Queue
            queue for sharing data from subprocess to master

        '''
        
        logger.debug('Process #%d started...' % os.getpid())

        # initialize xbeach model
        w = BMIWrapper('xbeach', configfile=parfile)
        w.initialize()

        # start listening loop
        while True:

            # get command from queue
            q = queue_to.get()

            if q:
                fcn, args = q
                try:
                    # execute command and put result to queue
                    r = getattr(w, fcn)(*args)
                    queue_from.put(r)
                except:
                    # command failed, log and put None to queue
                    logger.error('Call "%s" with "(%s)" FAILED [%d]' %
                                 (fcn, ','.join([str(x) for x in args]), os.getpid()))
                    queue_from.put(None)

                # register task as completed
                queue_to.task_done()

                # quit listening loop upon finalize
                if fcn == 'finalize':
                    break
                
                
    def __enter__(self):
        self.initialize()
        return self
    
    
    def __exit__(self, errtype, errobj, traceback):
        self.finalize()
        if errobj:
            raise errobj
        
        
    def get_current_time(self):
        return self._call('get_current_time')
    
    
    def get_start_time(self):
        return self._call('get_start_time')
    
    
    def get_end_time(self):
        return self._call('get_end_time')
    
    
    def get_var(self, var):
        return self._call('get_var', (var,))
    
    
    def get_var_name(self, i):
        raise NotImplemented(
            'BMI extended function "get_var_name" is not implemented yet')
    
    
    def get_var_count(self, var):
        return self._call('get_var_count', (var,))
    

    def get_var_rank(self, var):
        return self._call('get_var_rank', (var,))
    
    
    def get_var_shape(self, var):
        return self._call('get_var_shape', (var,))

    
    def get_var_type(self, var):
        return self._call('get_var_type', (var,))
    
    
    def inq_compound(self, var):
        raise NotImplemented(
            'BMI extended function "inq_compound" is not implemented yet')
    
    
    def inq_compound_field(self, var, field):
        raise NotImplemented(
            'BMI extended function "inq_compound_field" is not implemented yet')

    
    def set_var(self, var, val):
        if var == 'instance':
            self.set_instance(str(val))
        else:
            self._call('set_var', (var, val))
        
        
    def set_var_index(self, var, idx):
        raise NotImplemented(
            'BMI extended function "get_var_index" is not implemented yet')
        
    
    def set_var_slice(self, var, slc):
        raise NotImplemented(
            'BMI extended function "get_var_slice" is not implemented yet')

    
    def initialize(self):
        '''Initialize and start instance processes'''
        
        for name, instance in self.instances.iteritems():
            logger.debug('Starting process "%s"...' % name)
            self.instances[name]['process'] = \
                Process(target=self.run,
                        args=(instance['configfile'],
                              self.instances[name]['queue_to'],
                              self.instances[name]['queue_from']))
        self.start()
            
            
    def update(self, dt=-1):
        '''Update running instance and time'''
        
        self.update_instance()
        self._call('update', (dt,))
        if self.transition:
            if self._call('get_current_time') < self.transition['time']:
                for var, val in self.transition['vars'].iteritems():
                    self._call('set_var', (var, val))
            else:
                self.transition = None
                logger.info('Transition to instance "%s" finished.' % self.instance)
                    
        
    def finalize(self):
        '''Finalize instance processes'''
        
        for name, instance in self.instances.iteritems():
            logger.debug('Finalizing "%s"...' % name)
            self._call('finalize', instance=name)
        self.join()

        # change working directory back to original
        os.chdir(self.cwd)
        logger.debug('Changed directory to "%s"' % self.cwd)
        
        
    def _call(self, fcn, args=(), instance=None):
        '''Subprocess function caller

        Calls a function in a subprocess and returns the result via
        separate queues. If no instance is specified the running
        instance is used.

        Parameters
        ----------
        fcn : str
            name of function
        args : tuple
            function arguments
        instance : str
            name of instance for calling the function

        Returns
        -------
        any
            function result

        '''

        if not instance:
            instance = self.instance

        logger.debug('Call "%s" with "(%s)" [%d]' %
                     (fcn, ','.join([str(x) for x in args]), os.getpid()))
            
        self.instances[instance]['queue_to'].put((fcn, args))
        self.instances[instance]['queue_to'].join()
        return self.instances[instance]['queue_from'].get()

    
    @staticmethod
    def get_dimensions(var):
        '''Return dimensions of a given variable

        TODO: actually implement this function

        '''
        
        return (u'time', u'y', u'x')
