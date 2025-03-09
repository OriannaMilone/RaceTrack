import pandas as pd
import numpy as np

def driversDataProcessing():
    # Load the data
    drivers = pd.read_csv('SPA_DATA')
    drivers = drivers.drop(columns=['driverRef', 'number', 'code', 'url', 'dob', 'national