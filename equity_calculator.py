import pandas as pd
import numpy
import math


class EquityCalculator:
    def __init__(self, data):

        self.data = pd.read_excel(data, sheet_name="Summary")


    def calculate_weighted_equity(self, weights, equity_columns):
        """
        Calculate the weighted share for each row based on the input weights
        Inputs:
            weights: List of weights for each equity column
            equity_columns: List of column names to be weighted
        Returns:
            shares: pandas dataframe with countries, ISO codes and the weighted equity score


        """

        data = self.data[["Country", "ISO Code"] + equity_columns].copy()
        