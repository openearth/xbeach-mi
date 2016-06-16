import sys
import os
import json
import shutil
import logging
import traceback
import numpy as np
from mako.template import Template
from bmi.wrapper import BMIWrapper
from mpi4py import MPI
import progress, netcdf, parsers

from inspect import currentframe

def getln():  # get line number
    cf = currentframe()
    return cf.f_back.f_lineno


# initialize log
logger = logging.getLogger(__name__)


class XBeachMIWrapper:
    '''XBeachMIWrapper class

    Main class for XBeachMPI model wrapper. XBeachMPI is a wrapper for
    running multiple parallel instances of the XBeach program using the
    BMI interface.

    '''
    
    def __init__(self, configfile=None, mpicomm=None):
        '''Initialize the class

        Parameters
        ----------
        configfile : str
            path to JSON configuration file, see
            :func:`~beachmi.model.XBeachMPI.load_configfile`

        '''

        self.configfile = configfile
        self.comm = mpicomm
        self.rank = self.comm.rank

    def debug(self,s,x=()):
            lineno = currentframe().f_back.f_lineno
            ss = '%d line %d '+s+len(x)*' :: %s'
            logger.debug(ss%((self.comm.rank,lineno)+x))

    def run(self):
        '''Start model time loop'''

        with XBeachMPI(configfile=self.configfile,mpicomm=self.comm) as self.engine:

            self.t = 0

            endtime = self.engine.get_end_time()
            self.progress = progress.ProgressIndicator(duration=endtime)


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

            self.debug('Initializing output')
        
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

                self.debug('Writing output at t=' , (self.t,))
                
                # get dimension data for each variable
                variables = {v : self.engine.get_var(v) for v in cfg['outputvars']}
        
                if self.rank == 0:
                    variables['time'] = self.t
                    variables['instance'] = ', '.join(self.engine.running)
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
        if self.rank == 1:


            cfg_xbeach = parsers.XBeachParser(
                self.engine.instances[self.engine.running[0]]['configfile']).parse()

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
            

        dimensions = self.comm.bcast(dimensions,root=1)
        return dimensions

                
class XBeachMPI():
    '''Runs multiple instances of serial BMI XBeach processes,
    based on MPI.

    The class spwans a new process for every model instance. 
    A single model is updated at a time. If the running model 
    instance is changed data between the previous and the next 
    model instance is exchanged automatically.

    MPI processes:
      rank     task
      0        master process, performs input and creates netcdf output
      *        runs a xbeach process, communicating with the BMI protocol

    Instantation:
      x = XBeachMPI(configfile,mpicomm)
      configfile: see later
      mpicomm: MPI communicator to be used
          mpicomm must contain 1+number of xbeaches to be run

    Wrapped methods (to be called in mpicomm):

     - update(dt):         all processes are updated
     - get_end_time():     result (maximum of all ranks) is broadcasted 
                           to all processes in mpicomm
     - get_current_time(): result (maximum of all ranks) is broadcasted
     - get_var(var):       result is available on rank=0. It is the mean 
                           of the values for the running processes.
                           (Is this really what it should be?)
     - finalize()

    All BMI functions implemented in XBeach are available as: xbw.function()
      deleivering the result in the calling process.
    Note: process 0 does not define xbw.

    Extra methods:

     - get_dimensions(var): return (u'time', u'y', u'x')
     - read_dimensions():   is described in the code
     

    Available variables:

     - config:      the configuration file as a dict
     - running:     the running XBeach instances 

    The wrapper takes its own JSON configuration file that describes
    what instances should be created and at what moments in the
    simulation the running instance should be changed. See for more
    information on the configuration
    :func:`~xbeach-mi.model.XBeachMPI.load_configfile`.

    The params.txt file can be made instance dependent using the Mako
    templating system. See for more information on the templating
    options :func:`~xbeach-mi.model.XBeachMPI.load_configfile`.

    The XBeach library should be compiled with Position Independent
    Compilation (-fPIC compiler flag) in order to support local memory
    storage.

    '''

    engine = 'xbeach'
    running = []
    instances = {}
    next_index = 0
    next_aggregation = 0.
    data = {}
    
    dzmax = 0.05            # maximum bed level change per time step
    

    def __init__(self, configfile='',mpicomm=None):
        '''Initialize class

        Parameters
        ----------
        configfile : str
            path to JSON configuration file, see
            :func:`~xbeach-mi.model.XBeachMPI.load_configfile`

        '''
        
        self.comm = mpicomm
        self.rank = self.comm.rank
        self.config = {}
        self.configfile = configfile
        self.load_configfile()

    def debug(self,s,x=()):
            lineno = currentframe().f_back.f_lineno
            ss = '%d line %d '+s+len(x)*' :: %s'
            logger.debug(ss%((self.comm.rank,lineno)+x))

    def error(self,s,x=()):
            lineno = currentframe().f_back.f_lineno
            ss = '%d line %d '+s+len(x)*' :: %s'
            logger.error(ss%((self.comm.rank,lineno)+x))

    def handle_params_file(self):
        if not os.path.exists(self.config['params_file']):
            self.errer('no params_file')
            self.comm.Abort(1)
            sys.exit(1)

        # get instances
        instances = []
        if self.config.has_key('instances'):
            instances.extend(self.config['instances'])
        if self.config.has_key('scenario'):
            for t, i in self.config['scenario']:
                if type(i) is list:
                    instances.extend(i)
                else:
                    instances.append(i)
        instances = list(set(instances))

        # check if instances are defined
        if len(instances) == 0:
            print 'No instances defined, calling Abort()'
            self.comm.Abort()
            raise ValueError('No instances defined')

        if self.comm.size < len(instances)+1:
            print 'Number of instances found:',len(instances)
            print 'But number of processes is:',self.comm.size
            print 'Calling Abort()'
            self.comm.Abort()

        # not sure if the order in instances is the same on every
        # process, so bcast it:

        instances = self.comm.bcast(instances,0)

        # create a hash to couple ran to instance
        self.ranks = {}
        rank = 1
        for instance in instances:
            self.ranks[instance] = rank
            rank += 1


        # self.instance is the instance of this process

        if self.rank == 0:
            self.instance = None
        else:
            self.instance  = instances[self.rank-1]

        # set initial running instances

        self.running = list(instances)


        # create a hidden model directory for each model
        # instance listed in the configuration file and copy
        # params.txt file and other model configuration files
        # to the model directory

        # create instance variables
        for instance in instances:
            self.instances[instance] = {'process': None,
                                        'configfile': '',
                                        'markers': {}}

        # create hidden model directory
        if self.rank != 0:
            subdir = '.%s' % self.instance
            self.debug('Creating working directory' , (subdir,))
            if os.path.exists(subdir):
                shutil.rmtree(subdir)
            os.mkdir(subdir)

        # process 0 reads relevant files
        # these are bcasted and placed them in subdir

        files=[]
        fpath, fname = os.path.split(self.config['params_file'])
        if self.comm.rank == 0:
            if not os.path.isabs(fpath):
                fpath = os.path.join(os.getcwd(), fpath)
            files1 = os.listdir(fpath)
            for f in files1:
                if f[0] != '.' and f[-3:] != '.nc' and f[-4:] != '.log' and os.path.isfile(f):
                    files.append(f)

        files = self.comm.bcast(files,0)
        fc = ''
        for f in files:
            if self.comm.rank == 0:
                with open(os.path.join(fpath,f),'r') as fp:
                    fc = fp.read()
            fc = self.comm.bcast(fc,0)
            if self.rank != 0:
                with open(os.path.join(subdir,f),'w+') as fp:
                    fp.write(fc)
        del fc

        # create backup of original params.txt file
        if self.rank != 0:
            parfile  = os.path.join(subdir, fname)
            tmplfile = os.path.join(subdir, '%s.tmpl' % fname)
            shutil.copyfile(parfile, tmplfile)

            # store instance-specific mako template markers
            self.instances[self.instance]['markers'] = {
                'instance':self.instance,
                'path':os.path.abspath(subdir),
                'parfile':os.path.abspath(parfile),
                'tmplfile':os.path.abspath(tmplfile)
            }

            self.instances[self.instance]['configfile'] = os.path.abspath(parfile)

        # render templates


        if self.rank != 0:
            # set global mako template markers

            markers = self.instances[self.instance]['markers']


            markers['instances'] = self.instances.keys()

            self.debug('Rendering template' , (markers['tmplfile'],))
            
            template = Template(filename=markers['tmplfile'])
            with open(markers['parfile'], 'w') as fp:
                rendered = template.render(**markers)
                fp.write('defuse = 0\n') # disable time explosion checks
                fp.write(rendered)

        self.debug('Rendering complete')

    # end def handle_params_file():

    def load_configfile(self):
        '''Load JSON configuration file

        Loads JSON configuration file and create separate hidden model
        directories for each instance. The JSON configuration file may
        contain the following:

        .. literalinclude:: ../example/sequential/config.json
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
           
           % if instance.endswith('_morfac10'):
           morfac = 10
           % elif instance.endswith('_morfac100'):
           morfac = 100
           % endif

        Apart from the variable "instance" also the variables "path",
        "parfile" and "tmplfile" can be used in the params.txt
        template. These variables refer to the absolute model
        execution path, the absolute path to the rendered params.txt
        file and the absolute path to the params.txt template file
        used.

        '''

        # store current working directory
        self.cwd = os.getcwd()

        # reading config file is done by process 0
        if self.comm.rank == 0:
            if os.path.exists(self.configfile):

                self.debug('Reading configuration file' , (self.configfile,))


                # change working directry to location of configuration file
                if not os.path.isabs(self.configfile):
                    self.configfile = os.path.abspath(self.configfile)
                fpath, fname = os.path.split(self.configfile)
                os.chdir(fpath)
                self.debug('Changed directory to' ,(fpath,))

                # load configuration file
                with open(fname, 'r') as fp:
                    self.config = json.load(fp)
            else:
                print('Configuration file not found [%s]' % self.configfile)
                print('Will call self.comm.Abort()')
                self.comm.Abort()


        # bcast self.config

        self.config = self.comm.bcast(self.config,0)

        if self.config.has_key('engine'):
            self.engine = self.config['engine']

        if self.config.has_key('params_file'):
            self.handle_params_file()

    def update_instances(self):
        '''Change and/or update running instances'''


        if self.config.has_key('aggregate'):
            if self.config['aggregate'].has_key('interval'):
                t = self.xb_get_current_time()
                t = self.comm.bcast(t,root=0)
                if t >= self.next_aggregation:
                    self.set_instances(self.running)
                    self.next_aggregation = t + self.config['aggregate']['interval']
                    return

        if self.config.has_key('scenario'):
            if self.next_index < len(self.config['scenario']):
                t = self.xb_get_current_time()
                t = self.comm.bcast(t,root=0)
                tc, instances = self.config['scenario'][self.next_index]
                if not isinstance(instances,list):
                    instances = [instances]  # wwvv convert to []
                if t >= tc:
                    self.set_instances(instances)
                    self.next_index += 1
                    return


    def set_instances(self, instances):
        '''Change running instance, set time and exchange data

        Parameters
        ----------
        instances : list
            list of names of next running instances

        '''

        self.aggregate_data()   # data for 'var' is now in self.data['var'] on commrunning.rank == 0

        for instance in instances:
            if instance in self.instances.keys():
                self.sync_time(instance)
                self.exchange_data(instance,0)
            else:
                raise ValueError('Invalid instance [%s]' % instance)

        self.running = instances



    def sync_time(self, instance):
        '''Synchronize time between running instances and given instance

        Parameters
        ----------
        instance : str
            name of instance to be synced

        '''

        self.debug('Synchronizing time...',(instance,))
        
        # t1 will be max time of all processes in self.running
        try:
            t1 = self.xb_get_current_time()
        except:
            self.error('Failed to get time from' , (self.running))
            logger.error(traceback.format_exc())
            comm.Abort(1)
            sys.exit(1)


        # t2 will be the current time of instance 
        try:
            t2 = self.xb_get_current_time(instances=[instance])
        except:
            self.error('Failed to get time from' % (instance,))
            logger.error(traceback.format_exc())
            comm.Abort(1)
            sys.exit(1)


        if self.rank == 0:
            dt = t2-t1
        else:
            dt = None
        dt = self.comm.bcast(dt,root=0)
        
        try:
            self.xb_update(dt, instances=[instance])
        except:
            self.error('Failed to set time in' ,(instance,))
            logger.error(traceback.format_exc())
            comm.Abort(1)
            sys.exit(1)
        

    def aggregate_data(self):
        '''Aggregate exchange values of running instances and store in aggregated storage'''

        for var in self.config['exchange']:   # loop over variables to be aggregated

            self.debug('Aggregating' , (var,))

            try:
                val = self.xb_get_var(var)  # xg_get_var itself already aggregates

            except:
                self.error('Failed to get' , (self.instance,))
                logger.error(traceback.format_exc())
                comm.Abort(1)
                sys.exit(1)

            if self.rank == 0:
                self.data[var] = val
            

    def exchange_data(self, instance, senderrank):
        '''Exchange data from aggregated storage to given instance

        Parameters
        ----------
        instance : str
            name of instance to be updated

        '''

        for var in self.config['exchange']:
            self.debug('Exchanging' , (var,instance))

            receiverrank = self.ranks[instance]
            if self.rank == senderrank:
                self.comm.send(self.data[var], dest=receiverrank, tag=345)
            elif self.comm.rank == receiverrank:
                val = self.comm.recv(source=senderrank, tag=345)

                try:
                    self.xbw.set_var(var, val)
                except:
                    self.error('Failed to set var in instance' , (var, instance))
                    comm.Abort(1)
                    sys.exit(1)

            
    def aggregate(self, x, method='average', options={}):
        '''Aggregate values

        Parameters
        ----------
        x : tuple
            Tuple with values to be aggregated
        method : str
            Aggregation method (e.g. 'mean')
        options : dict
            Key/value pair options for aggregation method

        Returns
        -------
        misc
            Aggregated value of same type as original values in ``x``

        '''
        
        x = tuple([0 if i is None else i for i in x])
        if len(x) > 0:

            # read config
            if self.config.has_key('aggregate'):
                agg = self.config['aggregate']
                if agg.has_key('method'):
                    method = agg['method']
                if agg.has_key('options'):
                    options = agg['options']

            # apply aggregation
            if method == 'average':
                return np.average(x, axis=0, **options)
            else:
                raise ValueError('Unsupported aggregation method [%s]' % method)
    
                
    def __enter__(self):
        if self.rank != 0:
            self.xbw = BMIWrapper(self.engine, configfile=self.instances[self.instance]['configfile'])
            self.xbw.initialize()
        #self.test()
        return self

    def test(self):
        var='zb'
        if self.rank != 0:
            orig=self.xbw.get_var(var)
            self.debug(var,(orig.sum(),orig.dtype,orig.shape)) 
            y = np.random.random(orig.shape)
            self.debug('y',(y.sum(),y.dtype,y.shape)) 
            self.xbw.set_var(var,y)
            x=np.zeros_like(orig)
            self.debug(var,(var,x.sum(),x.dtype,x.shape)) 
            x=self.xbw.get_var(var)
            self.debug(var,(var,x.sum(),x.dtype,x.shape)) 

            t = self.xbw.get_current_time()
            self.debug('current time',(t,type(t)))

            self.debug('get nx')
            nx = self.xbw.get_var('nx')
            self.debug('nx',(nx,))

        self.debug('calling self.xb_get_var')
        x = self.xb_get_var(var,self.running)

        if x is None:
            self.debug(var,(var,x)) 
        else:
            self.debug(var,(var,x.sum(),x.dtype,x.shape)) 

        self.debug('calling self.xb_get_var from one process')
        for i in 0,1:
            x = self.xb_get_var(var,[self.instances.keys()[i]])

            if x is None:
                self.debug(var,(var,i,x)) 
            else:
                self.debug(var,(var,i,x.sum(),x.dtype,x.shape)) 

        if self.rank == 0:
            self.debug('calling self.xb_set_var',(var,x.shape,self.running))
        self.xb_set_var(var,x,self.running)

        if self.rank == 0:
            self.debug('calling self.xb_get_current_time')
        t = self.xb_get_current_time(self.running)
        self.debug('current time',(t,))

        if self.rank != 0:
            self.xbw.set_var(var,orig)

        self.debug('running',(self.running,))

        self.debug('calling xb_finalize')

        self.xb_finalize()
        sys.exit(0)

    
    
    def __exit__(self, errtype, errobj, traceback):
        self.xb_finalize()
        # get no usable traceback when following lines are uncommented:
        #if errobj:
        #    raise errobj
        
            

    def update(self, dt=-1):
        '''Update running instances and time

        All instances take one time step. Afterwards it is checked
        whether all instances are at the same point in time. If not,
        the lagging instances are updated further to match the given
        time step, if given, or the front runner instance otherwise.

        Parameters
        ----------
        dt : float
            Time step

        '''

        self.update_instances()

        try:
            if self.instance in self.running:
                t = self.xbw.get_current_time()
                self.xbw.update(dt)

            # determine target time
            if dt > 0.:
                target = t + dt
            else:
                if self.instance in self.running:
                    target = self.xbw.get_current_time()
                else:
                    target = 0

                target = self.comm.allreduce(target,op=MPI.MAX)

            # make sure all instances keep up with the front runner
            if self.instance in self.running:
                while True:
                    t = self.xbw.get_current_time()

                    if target > t:
                        self.xbw.update(target - t)
                    else:
                        break
            
        except:
            self.error('Failed to update' , (self.running,))
            logger.error(traceback.format_exc())
            comm.Abort(1)
            sys.exit(1)

            
    def xb_finalize(self):
        '''Finalize instance processes'''
        

        if self.rank != 0:
            self.xbw.finalize()

        # change working directory back to original

        os.chdir(self.cwd)
        self.debug('Changed directory to' , (self.cwd,))

    def finalize(self):
        self.xb_finalize()
        
    def xb_update(self,dt, instances = None):
        if self.rank == 0:
            return

        if not instances:
            instances = self.running

        if self.instance in instances:
            self.xbw.update(dt)
        

    def xb_get_var(self, var, instances=None):
        '''Returns aggregrated var from list instances
        Result is returned on self.rank == 0
        '''

        if not instances:
            instances = self.running

        if self.rank == 0:
            r = np.array([0])
        else:
            if self.instance in instances:
                r = self.xbw.get_var(var)
            else:
                r = np.array([0])

        # the aggregated output of the command is sent to process 0

        rr = self.comm.reduce(r, op=MPI.SUM, root=0)

        if self.rank == 0:
            return rr/len(instances)


        # todo: implement other aggregration types

    def get_var(self,var):
        return self.xb_get_var(var)


    def xb_get_current_time(self, instances=None):
        '''Returns aggregrated current time from list instances
        Result is returned on self.rank == 0
        '''

        if not instances:
            instances = self.running

        if self.rank == 0:
            r = 0
        else:
            if self.instance in instances:
                r = self.xbw.get_current_time()
            else:
                r = 0

        # the aggregated output of the command is sent to process 0

        rr = self.comm.reduce(r, op=MPI.MAX, root=0)
         
        if self.rank == 0:
            return rr

    def get_current_time(self):
        return(self.comm.bcast(self.xb_get_current_time(),root=0))

    def xb_get_end_time(self, instances=None):
        '''Returns aggregrated current time from list instances
        Result is returned on self.rank == 0
        '''

        if not instances:
            instances = self.running

        if self.rank == 0:
            r = 0
        else:
            if self.instance in instances:
                r = self.xbw.get_end_time()
            else:
                r = 0

        # the aggregated output of the command is sent to process 0


        rr = self.comm.reduce(r, op=MPI.MAX, root=0)
         
        if self.rank == 0:
            return rr

    def get_end_time(self):
        return self.comm.bcast(self.xb_get_end_time(),root=0)

    def xb_set_var(self, var, val, instances=None):
        '''Puts variable named var containing val on list instances '''

        if not instances:
            instances=self.running

        for inst in instances:
            receiverrank = self.ranks[inst]
            senderrank   = 0
            if self.rank == senderrank:
                self.comm.send(val,dest=receiverrank,tag=321)
            if self.rank == receiverrank:
                r = self.comm.recv(source=senderrank,tag=321)
                self.xbw.set_var(var,r)


    @staticmethod
    def get_dimensions(var):
        '''Return dimensions of a given variable

        TODO: actually implement this function

        '''
        
        return (u'time', u'y', u'x')
