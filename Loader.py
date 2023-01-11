#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import time
import re
import numpy as np
import glob
import pandas as pd

from PyQt5.QtCore import (
    QObject, pyqtSignal
    )


# data ######################################################################

class Loader(QObject):


    def __init__(self, csv_file):

        print("Loader -- create object")
        super().__init__()
        self.csv_file = csv_file
        self.open()
        print("Loader -- create object -- finished")

    def open(self):
        """
        Open csv file and write in dictionary 
        ----------
        filename : fullpth csv file

        """
        print("Loader -- Open file")

        with open(self.csv_file, 'r') as f:
            # images_data = pd.read_csv(f, sep=',').to_dict()
            images_data = pd.read_csv(f, sep=',')
            # replace NaN values with 0
            self.images_data = images_data.fillna(0)
            self.images_data = images_data.to_dict()

            # Keep a trace of the original data
            self.images_data_mem = self.images_data
            # Record number of data 
            self.images_number = len(self.images_data['folder'])


        print("Loader -- Open file finished")


















            