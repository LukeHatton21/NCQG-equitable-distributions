import streamlit as st
from  streamlit_vertical_slider import vertical_slider 
from equity_calculator import EquityCalculator
from visualiser import Visualiser

st.title(":earth_africa: Equity in Climate Finance Calculator")
st.write(
    "This tool allows exploration of the impact of different equity criterion on the distribution of climate finance for mitigation, adaptation and loss and damages across developing countries, for either the UNFCCC NCQG or another specified total quantum."
)

total_value = st.number_input("Total Climate Finance (USDbn)", min_value=0, max_value=500, value=300)
col1, col2 = st.columns(2)
with col1:
    exclude_US = st.checkbox("Exclude USA from contributions", value=True, key="Exclude_USA")
with col2:
    include_UMIC = st.checkbox("Include UMIC as contributors", value=True, key="Include_UMIC")

# Call visualiser and equity calculator classes
equity_calculator = EquityCalculator(data="NCQG Data.xlsx")
visualiser = Visualiser()
tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs(["📍 Weighting", "📊 Allocations", "📈 Contributions", "🗺️ Regional Distribution" , "🌐 Map", "ℹ️ About"])
with tab0:
    st.title("Equity Considerations")
    variables = visualiser.variable_selection(equity_calculator)
    st.write(variables)
    weights_mapping = visualiser.weights_input()
    if None not in variables:
        calculated_flows = equity_calculator.calculate_weighted_equity(weights_mapping, variables, total_value)
        calculated_contributions = equity_calculator.calculate_contributions(weights_mapping, variables, total_value, include_UMIC=include_UMIC, exclude_US=exclude_US)
with tab1:
    st.title("Climate Finance Recipient Flows")
    if None not in variables:
        visualiser.plot_ranking_table(calculated_flows, "Allocation_USDbn")
        regional_flows = equity_calculator.aggregate_to_regions(calculated_flows)
        visualiser.plot_ranking_table(regional_flows, "Allocation_USDbn")
with tab2: 
    st.title("Climate Finance Contributions")
    if None not in variables:
        visualiser.plot_ranking_table(calculated_contributions, "Contributions_USDbn")
with tab3: 
    st.write("AGGREGATE AND INCLUDE")
with tab4: 
    st.write("INCLUDE MAP FROM LCOH")
with tab5:
    st.write("INCLUDE DETAILS")