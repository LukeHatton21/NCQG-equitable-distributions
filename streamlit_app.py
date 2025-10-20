import streamlit as st
from  streamlit_vertical_slider import vertical_slider 
from equity_calculator import EquityCalculator
from visualiser import Visualiser

st.title(":earth_africa: Equity in Climate Finance Calculator")
st.write(
    "This tool allows exploration of the impact of different equity criterion on the distribution of climate finance for mitigation, adaptation and loss and damages across developing countries, for either the UNFCCC NCQG or another specified total quantum."
)
st.number_input("Total Climate Finance (USDbn)", min_value=0, max_value=500, value=300)


# Call visualiser and equity calculator classes
equity_calculator = EquityCalculator(data="NCQG Data.xlsx")
visualiser = Visualiser()
tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs(["Weighting", "📊 Allocations", "Comparison", "🗺️ Regional Distribution" , "🌐 Map", "ℹ️ About"])
with tab0:
    st.title("Equity Considerations")
    visualiser.variable_selection()
    visualiser.weights_input()
with tab1:
    st.write("INCLUDE TABLE")
with tab2: 
    st.write("INCLUDE DAC FLOWS")
with tab3: 
    st.write("AGGREGATE AND INCLUDE")
with tab4: 
    st.write("INCLUDE MAP FROM LCOH")
with tab5:
    st.write("INCLUDE DETAILS")