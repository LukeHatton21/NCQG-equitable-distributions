import pandas as pd
import streamlit as st
from  streamlit_vertical_slider import vertical_slider 
import numpy as np
import altair as alt


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
        default_value = 2
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
        with col2:
            capacity = st.selectbox(
                        "Capacity", (list(equity_calculator.capacity_dict.keys())), 
                        index=None, key="Capacity_Var", placeholder="Select Capacity...")
        with col3:
            needs = st.selectbox(
                        "Needs", (list(equity_calculator.needs_dict.keys())), 
                        index=None, key="Needs_Var", placeholder="Select Needs...")
            
        with col4:
            engagement = st.selectbox(
                        "Engagement", (list(equity_calculator.engagement_dict.keys())), 
                        index=None, key="Engagement_Var", placeholder="Select Engagement...")
        
        selected_variables = [responsibility, capacity, needs, engagement]

        return selected_variables


    def plot_ranking_table(self, dataframe, value_column):


        # Melt dataframe
        df = dataframe[["Country", "ISO", value_column]].copy()
        df = df.rename(columns={value_column: "Value", "ISO":"Country code"})

        # Create chart
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('sum(Value):Q', stack='zero', title='Annual flows (USD billion)'),
            y=alt.Y('Country code:O', sort="-x", title='Country'),
              tooltip=[
        alt.Tooltip('Country:N', title='Country'),  # <-- show country name
        alt.Tooltip('sum(Value):Q', title='Value (USD bn)', format='0.1f')]  # Sort countries by total value descending
    ).properties(width=700)

        # Add x-axis to the top
        x_axis_top = chart.encode(
            x=alt.X('sum(Value):Q', stack='zero', title='', axis=alt.Axis(orient='top'))
        )

        # Combine the original chart and the one with the top axis
        chart_with_double_x_axis = alt.layer(
            chart,
            x_axis_top
        )

        st.write(chart_with_double_x_axis)