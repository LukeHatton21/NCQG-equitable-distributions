import pandas as pd
import numpy
import math


class EquityCalculator:
    def __init__(self, data):

        self.data = pd.read_excel(data, sheet_name="Summary")
        self.responsibility_dict = {
            "Cumulative Emissions since 1850": "X1850_2022",
            "Cumulative Emissions since 1950": "X1990_2022",
            "Cumulative Emissions per capita": "GHG_historical_pc"
        }
        self.capacity_dict = {
            "Gross National Income":"GNI_avg",
            "Gross National Income minus debt": "GNI_debt_avg",
            "Gross National Income per capita": "GNI_PPP_pv_avg"
        }
        self.needs_dict = {
            "Climate Risk and Vulnerability Index": "GAIN_CR",
            "Physical Climate Risk (EIB)": "EIB_PR"
        }
        self.engagement_dict = {
            "UN Multilateral Engagement Score": "UN Index"
        }
        self.variable_dict =  {**self.responsibility_dict, **self.capacity_dict, **self.needs_dict, **self.engagement_dict}

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
        