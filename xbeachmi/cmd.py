'''xbeach-mi : XBeach wrapper for running multiple parallel instances

Usage:
    xbeach-mi <config> [--verbose=LEVEL]

Positional arguments:
    config             configuration file

Options:
    -h, --help         show this help message and exit
    --verbose=LEVEL    print logging messages [default: DEBUG]

'''

from mpi4py import MPI

import sys
import os
import logging
from model import XBeachMIWrapper

def logleveltonumber(s1):
    s = s1.upper()
    if s == 'INFO':
        return logging.INFO
    elif s == 'DEBUG':
        return logging.DEBUG
    elif s == 'WARNING':
        return logging.WARNING
    elif s == 'ERROR':
        return logging.ERROR
    elif s == 'CRITICAL':
        return logging.CRITICAL
    else:
        return logging.NOTSET


def cmd():
    comm = MPI.COMM_WORLD
    arguments={}
    import docopt
    if comm.rank == 0:
        arguments = docopt.docopt(__doc__)

    arguments = comm.bcast(arguments,0)
    # initialize logger
    if arguments['--verbose'] is not None:
        logging.basicConfig(format='%(name)-8s %(levelname)-8s %(message)s')
        logging.root.setLevel(logleveltonumber(arguments['--verbose']))
    else:
        logging.root.setLevel(logging.DEBUG)  # or NOTSET


    logger=logging.getLogger(__name__)
    if comm.rank == 0:
        logger.info('started!')
        logger.debug('debug started!')
    comm.Barrier()
    logger.debug('size,rank %d %d',comm.size,comm.rank)
    comm.Barrier()
    # start model
    XBeachMIWrapper(configfile=arguments['<config>'],mpicomm=comm).run()

            
if __name__ == '__main__':
    print 'cmd started in rank',MPI.COMM_WORLD.rank
    print
    cmd()
    print 'cmd ended in rank',MPI.COMM_WORLD.rank
    
