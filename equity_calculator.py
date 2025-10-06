import pandas
import numpy
import math


class EquityCalculator:
    def __init__(self, data):

        self.data = pd.read_excel(data, sheet_name="Summary")