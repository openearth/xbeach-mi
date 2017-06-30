from __future__  import absolute_import

import docopt
import logging

from xbeachmi.model import XBeachMIWrapper


def xbeachmi_prepare():
    '''xbeach-mi-prepare : preparation tool for XBeach orchestrator

Usage:
    xbeach-mi-prepare <config> [options]

Positional arguments:
    config             configuration file

Options:
    -h, --help         show this help message and exit
    --verbose=LEVEL    print logging messages [default: 30]

    '''
    
    arguments = docopt.docopt(xbeachmi_prepare.__doc__)

    # initialize logger
    if arguments['--verbose'] is not None:
        logging.basicConfig(format='%(asctime)-15s %(name)-8s %(levelname)-8s %(message)s')
        logging.root.setLevel(int(arguments['--verbose']))
    else:
        logging.root.setLevel(logging.NOTSET)

    # prepare model
    XBeachMIWrapper(configfile=arguments['<config>']).prepare()


def xbeachmi_spawn():
    '''xbeach-mi-spawn : spawn MMI clients for XBeach orchestrator

Usage:
    xbeach-mi-spawn <config> [options]

Positional arguments:
    config             configuration file

Options:
    -h, --help         show this help message and exit
    --verbose=LEVEL    print logging messages [default: 30]

    '''
    
    arguments = docopt.docopt(xbeachmi_prepare.__doc__)

    # initialize logger
    if arguments['--verbose'] is not None:
        logging.basicConfig(format='%(asctime)-15s %(name)-8s %(levelname)-8s %(message)s')
        logging.root.setLevel(int(arguments['--verbose']))
    else:
        logging.root.setLevel(logging.NOTSET)

    # prepare model
    XBeachMIWrapper(configfile=arguments['<config>']).spawn()


def xbeachmi():
    '''xbeach-mi : XBeach wrapper for running multiple parallel instances

Usage:
    xbeach-mi <config> [options]

Positional arguments:
    config             configuration file

Options:
    -h, --help         show this help message and exit
    --overwrite        allow overwriting of run directories
    --verbose=LEVEL    print logging messages [default: 30]

    '''
    
    arguments = docopt.docopt(xbeachmi.__doc__)

    # initialize logger
    if arguments['--verbose'] is not None:
        logging.basicConfig(format='%(asctime)-15s %(name)-8s %(levelname)-8s %(message)s')
        logging.root.setLevel(int(arguments['--verbose']))
    else:
        logging.root.setLevel(logging.NOTSET)

    # run model
    XBeachMIWrapper(configfile=arguments['<config>']).run(overwrite=bool(arguments['--overwrite']))

            
if __name__ == '__main__':
    xbeachmi()
    
