import time
import logging
from numpy import mod


class ProgressIndicator:


    fmt = '[%5.1f%%] %s / %s / %s (avg. dt=%5.3f)'
    spaces = {}
    default_space = None


    def __init__(self, duration=3600., fraction=.1, interval=60., spaces=['log', 'output']):
        '''Initialize class
        
        Parameters
        ----------
        duration : float
            duration of simulation
        fraction : float
            fraction of simulation duration used to display progress
        interval : float
            maximum time interval to not display any progress
        spaces : list
            list of namespaces each being a progress counter
            
        '''

        self.start = time.time() # in real-world time
        self.duration = duration # in simulation time
        self.fraction = fraction
        self.interval = interval # in real-world time
        self.last = 0. # in simulation time
        self.i = 1

        t0 = time.time() # in real-world time
        for space in spaces:
           self.spaces[space] = t0
           if not self.default_space:
               self.default_space = space
        

    def progress(self, t):
        '''Log progress
                  
        Parameters
        ----------
        t : float
            current time
                        
        '''

        if len(self.spaces) == 0:
            return
        
        if self.check_fraction(t, self.fraction) or \
           self.check_time(self.interval):

            p = min(1, t / self.duration)
            dt1 = time.time() - self.start
            dt2 = dt1 / p
            dt3 = dt2 * (1-p)
            
            if p <= 1:
                logging.info(self.fmt % (p*100.,
                                         time.strftime('%H:%M:%S', time.gmtime(dt1)),
                                         time.strftime('%H:%M:%S', time.gmtime(dt2)),
                                         time.strftime('%H:%M:%S', time.gmtime(dt3)),
                                         t / self.i))

                self.touch_space()
                
        self.i += 1
        self.last = t


    def check_fraction(self, t, fraction):
        '''Check if fraction of simulation time has passed'''

        return self.check_period(t, self.duration * fraction)


    def check_period(self, t, interval):
        '''Check if interval in simulation has passed'''
        
        return mod(t, interval) < t - self.last


    def check_time(self, interval, space=None):
        '''Check if certain amount of time has passed'''

        if not space:
            space = self.default_space

        return time.time() - self.spaces[space] > interval


    def touch_space(self, space=None):
        '''Register space as updated'''

        if not space:
            space = self.default_space

        self.spaces[space] = time.time()

