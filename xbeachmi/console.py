import docopt
import logging
from model import XBeachMIWrapper


def xbeachmi():
    '''xbeach-mi : XBeach wrapper for running multiple parallel instances

Usage:
    xbeach-mi <config> [--verbose=LEVEL]

Positional arguments:
    config             configuration file

Options:
    -h, --help         show this help message and exit
    --verbose=LEVEL    print logging messages [default: 30]

    '''
    
    arguments = docopt.docopt(xbeachmi.__doc__)

    # initialize logger
    if arguments['--verbose'] is not None:
        logging.basicConfig(format='%(asctime)-15s %(name)-8s %(levelname)-8s %(message)s')
        logging.root.setLevel(int(arguments['--verbose']))
    else:
        logging.root.setLevel(logging.NOTSET)

    # start model
    XBeachMIWrapper(configfile=arguments['<config>']).run()

            
if __name__ == '__main__':
    xbeachmi()
    
