import pandas as pd
import streamlit as st
import itertools
import numpy as np


class EquityCalculator:
    def __init__(self, data):

        self.data = pd.read_excel(data, sheet_name="Summary")
        self.responsibility_dict = {
            "Cumulative Emissions since 1850": "X1850_2024",
            "Cumulative Emissions since 1950": "X1990_2024",
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

    def calculate_robust_allocation(self):


        data = self.data.loc[self.data["AnnexII_countries"]==0].copy()
        weight_values = np.linspace(0, 1, 6)
        iteration = 0 
        summary_dict = {} 
        for (resp_name, resp_col), (cap_name, cap_col), (need_name, need_col), (eng_name, eng_col) \
            in itertools.product(self.responsibility_dict.items(),
            self.capacity_dict.items(),
            self.needs_dict.items(),
            self.engagement_dict.items()):
            
            variable_columns = [resp_name, cap_name, need_name, eng_name]
            equity_columns = [resp_col, cap_col, need_col, eng_col]
            for w_resp, w_capacity, w_needs, w_engagement in itertools.product(weight_values, repeat=4):
                
                iteration += 1
                iter_name = f"RUN{iteration}"
                
                # Normalize the weights
                weights = [w_resp, w_capacity, w_needs, w_engagement]

                for variable in variable_columns:
                    column = self.variable_dict[variable]
                    data = self.calculate_share(data, column, variable)
        
                # Calculate weighted equity score
                data["Weighted_equity_share"] = data[[col + "_share" for col in equity_columns]]\
                    .multiply(weights).sum(axis=1) \
                        / sum(weights)

                # Calculate allocations
                data["Share_RUN"+iter_name] = data["Weighted_equity_share"]

                # Drop all intermediate columns
                data = data.drop(columns=[col for col in data.columns if col.endswith("_share")])

                # Store parameters
                summary_dict[iter_name] = {
        "responsibility_metric": resp_name,
        "responsibility_column": resp_col,
        "w_responsibility": w_resp,

        "capacity_metric": cap_name,
        "capacity_column": cap_col,
        "w_capacity": w_capacity,

        "needs_metric": need_name,
        "needs_column": need_col,
        "w_needs": w_needs,

        "engagement_metric": eng_name,
        "engagement_column": eng_col,
        "w_engagement": w_engagement}
                    
        # Calculate average share across all iterations
        data["Robust_Share"] = data[[col for col in data.columns if col.startswith("Share_RUN")]].mean(axis=1)
        summary_df = pd.DataFrame.from_dict(summary_dict, orient="index")

        # Save file
        summary_df.to_csv("Robust_Allocations_NCQG.csv")


        return data, summary_df


    def calculate_robust_contributions(self, include_UMIC=None, exclude_US=None):

        # Get relevant data
        if include_UMIC == True:
            selected_data = self.data.loc[self.data["above_middle_countries"] == 1]
        else:
            selected_data = self.data.loc[self.data["AnnexII_countries"] == 1]

        # Remove US if specified
        if exclude_US is True:
            selected_data = selected_data.loc[selected_data["ISO"] != "USA"]
        
        weight_values = np.linspace(0, 1, 6)
        iteration = 0 
        summary_dict = {} 
        for (resp_name, resp_col), (cap_name, cap_col), (need_name, need_col), (eng_name, eng_col) \
            in itertools.product(self.responsibility_dict.items(),
            self.capacity_dict.items(),
            self.needs_dict.items(),
            self.engagement_dict.items()):
            
            variable_columns = [resp_name, cap_name, need_name, eng_name]
            equity_columns = [resp_col, cap_col, need_col, eng_col]
            for w_resp, w_capacity, w_needs, w_engagement in itertools.product(weight_values, repeat=4):
                
                iteration += 1
                iter_name = f"RUN{iteration}"
                
                # Normalize the weights
                weights = [w_resp, w_capacity, w_needs, w_engagement]

                for i, variable in enumerate(variable_columns):
                    column = self.variable_dict.get(variable)
                    basis = self.variable_calculations.get(variable)
                    
                    if basis == "positive":
                        data[column + "_contribution"] = (1/data[column]) / (1/data[column]).sum()
                    elif basis == "negative":
                        data[column + "_contribution"] = data[column] / data[column].sum()  
        
                
                
                # Calculate weighted equity score
                data["Weighted_Contributions_Score"] = data[[col + "_contribution" for col in equity_columns]]\
            .multiply(weights).sum(axis=1) \
                / sum(weights)

                # Calculate allocations
                data["Share_RUN"+iter_name] = data["Weighted_Contributions_Score"]

                # Drop all intermediate columns
                data = data.drop(columns=[col for col in data.columns if col.endswith("_share")])

                # Store parameters
                summary_dict[iter_name] = {
        "responsibility_metric": resp_name,
        "responsibility_column": resp_col,
        "w_responsibility": w_resp,

        "capacity_metric": cap_name,
        "capacity_column": cap_col,
        "w_capacity": w_capacity,

        "needs_metric": need_name,
        "needs_column": need_col,
        "w_needs": w_needs,

        "engagement_metric": eng_name,
        "engagement_column": eng_col,
        "w_engagement": w_engagement}
                    
        # Calculate average share across all iterations
        data["Robust_Contributions"] = data[[col for col in data.columns if col.startswith("Share_RUN")]].mean(axis=1)
        summary_df = pd.DataFrame.from_dict(summary_dict, orient="index")
        
        # Save file
        summary_df.to_csv("Robust_Contributions_NCQG.csv")


        return data, summary_df

