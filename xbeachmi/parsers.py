import os
import re
import numpy as np


class ConfigParser:
    '''Configuration parser base class

    Base class for the construction of model engine configuration file
    parsers. Parses the main configuration file and referenced files
    therin.

    '''
    
    def __init__(self, configfile):
        '''Initialize the class

        Parameters
        ----------
        configfile : str
            path to model configuration file

        '''
        
        self.configfile = configfile

        
    def parse(self):
        '''Parse configuration file

        Returns
        -------
        dict
            key/value pairs of model configuration

        '''

        return self.parse_config_file(self.configfile)
    

    def parse_config_file(self, configfile):
        '''Parse configuration file

        Parameters
        ----------
        configfile : str
            path to configuration file

        Returns
        -------
        dict
            key/value pairs of model configuration

        '''

        config = {}
        with open(configfile, 'r') as fp:
            for line in fp:
                if '=' in line:
                    key, value = re.split('\s*=\s*', line, maxsplit=1)
                    key = key.strip()
                    value = self.parse_config_value(value)
                    
                    if type(value) is str and os.path.exists(value):
                        value = self.parse_referenced_file(value)

                    config[key] = value

        return config


    def parse_referenced_file(self, fname):
        '''Parse a file referenced in the main configuration file

        Parameters
        ----------
        fname : str
            referenced filename

        Returns
        -------
        np.ndarray, dict or list
            a np.ndarray for numeric data, a dictionary for key/value
            data or a list for plain text data

        '''

        data = []
        
        try:
            data = np.loadtxt(fname)
            return data
        except:
            pass

        try:
            data = self.parse_config_file(fname)
            return data
        except:
            pass

        try:
            data = []
            with open(fname, 'r') as fp:
                for line in fp:
                    data.append(line)
        except:
            pass
            

    @staticmethod
    def parse_config_value(value, force_list=False):
        '''Parse configuration value string to valid Python variable type

        Parameters
        ----------
        value : str
            configuration value string

        Returns
        -------
        str, int, float, bool or list
            parsed configuration value

        '''

        value = value.strip()
        if re.search('\s', value) or force_list:
            return [self.parse_config_value(x) for x in re.split('\s+', value)]
        elif re.match('[FT]$', value):
            return value == 'T'
        elif re.match('[\-0-9]+$', value):
            return int(value)
        elif re.match('[\-0-9\.]+$', value):
            return float(value)
        else:
            return value


class XBeachParser(ConfigParser):
    '''Configuration parser class for XBeach models

    Inherits from :class:`ConfigParser`.

    '''
    
    pass
