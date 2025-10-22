import pandas as pd
import streamlit as st
from  streamlit_vertical_slider import vertical_slider 

class Visualiser():
    def __init__(self):
        pass


    def weights_input(self):
        equity_columns = [
            "Responsibility",
            "Capacity",
            "Needs",
            "Engagement",
        ]

        col1, col2, col3, col4 = st.columns(4)
        col_list = [col1, col2, col3, col4]
        default_value = 1
        max_value = 20

        # Calculate inputs
        weights = []
        for i, column in enumerate(equity_columns):
            with col_list[i]:
                weight = vertical_slider(
                    label=column,
                    min_value=0,
                    max_value=max_value,
                    default_value=default_value,
                    step=1,
                    key=column,
                )
                weights.append(weight)

        return dict(zip(equity_columns, weights))

    def variable_selection(self, equity_calculator):

        col1, col2= st.columns(2)
        col3, col4 = st.columns(2)
        # Take inputs for each category
        with col1:
            responsibility = st.selectbox(
                        "Responsibility", (list(equity_calculator.responsibility_dict.keys())), 
                        index=None, key="Responsibility_Var", placeholder="Select Responsibility...")
            responsibility = equity_calculator.variable_dict[responsibility]
        with col2:
            capacity = st.selectbox(
                        "Capacity", (list(equity_calculator.capacity_dict.keys())), 
                        index=None, key="Capacity_Var", placeholder="Select Capacity...")
            capacity = equity_calculator.variable_dict[capacity]
        with col3:
            needs = st.selectbox(
                        "Needs", (list(equity_calculator.needs_dict.keys())), 
                        index=None, key="Needs_Var", placeholder="Select Needs...")
            needs = equity_calculator.variable_dict[needs]
            
        with col4:
            engagement = st.selectbox(
                        "Engagement", (list(equity_calculator.engagement_dict.keys())), 
                        index=None, key="Engagement_Var", placeholder="Select Engagement...")
            engagement = equity_calculator.variable_dict[engagement]
        
        selected_variables = [responsibility, capacity, needs, engagement]

        return selected_variables