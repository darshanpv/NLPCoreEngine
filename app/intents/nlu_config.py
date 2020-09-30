# -*- coding: utf-8 -*-
import os
from warnings import simplefilter

# ignore all warnings
simplefilter(action='ignore')

##Global parameters
scriptDir = os.path.dirname(__file__)

dataPath = os.path.join(scriptDir, 'data')
propertyFile = os.path.join(scriptDir, 'config', 'nlu.properties')

separator = "="

class NLU_config:
    properties = {}

    def __init__(self):
        pass

    def _check_data_avaialble(self) -> bool:
        files = os.listdir(dataPath)
        for file in files:
            if (file.startswith(self.domain)):
                if file.endswith(self.format):
                    return True
            else:
                pass
        return False

    def _get_config_parameter(self) -> None:
        self.properties = {}
        with open(propertyFile) as f:
            for line in f:
                if separator in line:
                    name, value = line.split(separator, 1)
                    self.properties[name.strip()] = value.strip()
        if 'format' in self.properties:
            self.format = self.properties.get('format')
        if 'algorithm' in self.properties:
            self.algorithm = self.properties.get('algorithm')
        if 'config_file' in self.properties:
            self.config_file = self.properties.get('config_file')

    def _get_configuration(self, domain):
        self.domain = domain
        self._get_config_parameter()
        if self._check_data_avaialble():
            self.isDataFileAvailable = True
        else:
            self.isDataFileAvailable = False