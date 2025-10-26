import pandas as pd
import streamlit as st


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
            "Gross National Income per capita": "GNI_PPP_pc_avg"
        }
        self.needs_dict = {
            "Climate Risk and Vulnerability Index": "GAIN_CR",
            "Physical Climate Risk (EIB)": "EIB_PR"
        }
        self.engagement_dict = {
            "UN Multilateral Engagement Score": "UN Index"
        }
        self.variable_dict =  {**self.responsibility_dict, **self.capacity_dict, **self.needs_dict, **self.engagement_dict}
        self.variable_calculations = self.set_variable_calculations()
        
    
    def set_variable_calculations(self):

        mapping_dicts = {
            'negative': [self.responsibility_dict, self.capacity_dict],
            'positive': [self.needs_dict, self.engagement_dict]
        }

        calculation_basis = {}

        for label, dict_list in mapping_dicts.items():
            for d in dict_list:
                for key in d:
                    calculation_basis.setdefault(key, []).append(label)

        calculation_basis = {
            k: v[0] if len(v) == 1 else v
            for k, v in calculation_basis.items()
        }

        return calculation_basis

    def calculate_weighted_equity(self, weights, variable_columns, value):
        """
        Calculate the weighted share for each row based on the input weights
        Inputs:
            weights: List of weights for each equity column
            equity_columns: List of column names to be weighted
        Returns:
            shares: pandas dataframe with countries, ISO codes and the weighted equity score


        """

        # Remove Annex II countries
        data = self.data.loc[self.data["AnnexII_countries"]==0]

        # Get relevant columns
        equity_columns = [self.variable_dict[k] for k in variable_columns]
        data = data[["Country", "ISO", "Region"] + equity_columns].copy()

        # Calculate shares for each equity column
        for variable in variable_columns:
            column = self.variable_dict[variable]
            data = self.calculate_share(data, column, variable)
        
        # Calculate weighted equity score
        data["Weighted_Equity_Score"] = data[[col + "_share" for col in equity_columns]]\
            .multiply(list(weights.values())).sum(axis=1) \
                / sum(list(weights.values()))

        # Calculate allocation
        data["Allocation_USDbn"] = data["Weighted_Equity_Score"] * value
        st.write(data)

        return data

    def calculate_share(self, data, column, variable):

        # Get calculation basis
        basis = self.variable_calculations.get(variable)

        # Calculate share based on basis
        if basis == 'positive':
            data[column + "_share"] = data[column] / data[column].sum()

        elif basis == 'negative':
            data[column + "_share"] = (1/data[column]) / (1/data[column]).sum()
                                           
        else:
            raise ValueError("No valid basis found in the mapping")
        
        return data


    def calculate_contributions(self, weights, variable_columns, total_value, include_UMIC=None, exclude_US=None):
        """
        Calculate the contributions of either Annex II or all UMIC/HIC countries to the NCQG
        
        Inputs:
            weights: List of weights for each equity column (Responsibility, Capacity, Needs, Engagement)
            variable_columns: List of selected variable names
            total_value: Total climate finance value (USDbn)

        """

        # Get relevant data
        if include_UMIC == True:
            selected_data = self.data.loc[self.data["above_middle_countries"] == 1]
        else:
            selected_data = self.data.loc[self.data["AnnexII_countries"] == 1]

        # Remove US if specified
        if exclude_US is True:
            selected_data = selected_data.loc[selected_data["ISO"] != "USA"]
        
        # Remove needs and engagement from the calculation
        responsibility = weights.get("Responsibility")
        capacity = weights.get("Capacity")
        weights = [responsibility, capacity]
        variable_columns = variable_columns[0:2]

         # Get relevant columns
        equity_columns = [self.variable_dict.get(k) for k in variable_columns]
        data = selected_data[["Country", "ISO", "Region"] + equity_columns].copy()

        # Calculate contributions
        for i, variable in enumerate(variable_columns):
            column = self.variable_dict.get(variable)
            basis = self.variable_calculations.get(variable)
            
            if basis == "positive":
                data[column + "_contribution"] = (1/data[column]) / (1/data[column]).sum()
            elif basis == "negative":
                data[column + "_contribution"] = data[column] / data[column].sum()  

        # Calculate weighted equity score for contributions
        data["Weighted_Contributions_Score"] = data[[col + "_contribution" for col in equity_columns]]\
            .multiply(weights).sum(axis=1) \
                / sum(weights)

        # Calculate allocation
        data["Contributions_USDbn"] = data["Weighted_Contributions_Score"] * total_value

        return data
    
    def aggregate_to_regions(self, data):

        # Aggregate to regions
        region_data = data.groupby("Region").agg({
            "Allocation_USDbn": "sum"
        }).reset_index()

        # Set up country and ISO codes
        region_data["ISO"] = region_data["Region"]
        region_data["Country"] = region_data["Region"]

        # Return data
        return region_data
