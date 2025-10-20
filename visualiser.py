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

    def variable_selection(self):

        col1, col2, col3, col4 = st.columns(4)

        # Take inputs for each category
        with col1:
            responsibility = st.selectbox(
                        "Responsibility", (""), 
                        index=None, key="Responsibility_Var", placeholder="Select Responsibility...")
        with col2:
            capacity = st.selectbox(
                        "Capacity", (""), 
                        index=None, key="Capacity_Var", placeholder="Select Capacity...")
        with col3:
            needs = st.selectbox(
                        "Needs", (""), 
                        index=None, key="Needs_Var", placeholder="Select Needs...")
        with col4:
            engagement = st.selectbox(
                        "Engagement", (""), 
                        index=None, key="Engagement_Var", placeholder="Select Engagement...")