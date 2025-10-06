import streamlit as st
from  streamlit_vertical_slider import vertical_slider 
from equity_calculator import EquityCalculator

st.title(":earth_africa: Equity in Climate Finance Calculator")
st.write(
    "This tool allows exploration of the impact of different equity criterion on the distribution of climate finance for mitigation, adaptation and loss and damages across developing countries, for either the UNFCCC NCQG or another specified total quantum."
)
st.number_input("Total Climate Finance (USDbn)", min_value=0, max_value=500, value=300)

st.title("Importance of Different Equity Considerations")
col1, col2, col3, col4 = st.columns(4)
default_value = 1
max_value = 5
with col1:
    vertical_slider(
    label = "Responsibility",  #Optional
    key = "vert_01" ,
    height = 300, #Optional - Defaults to 300
    thumb_shape = "square", #Optional - Defaults to "circle"
    step = 1, #Optional - Defaults to 1
    default_value=default_value ,#Optional - Defaults to 0
    min_value= 0, # Defaults to 0
    max_value= max_value , # Defaults to 10
    track_color = "blue", #Optional - Defaults to Streamlit Red
    slider_color = ('red','blue'), #Optional
    thumb_color= "orange", #Optional - Defaults to Streamlit Red
    value_always_visible = True ,#Optional - Defaults to False
    )

with col2:
    vertical_slider(
    label = "Capaciy",  #Optional
    key = "vert_02" ,
    height = 300, #Optional - Defaults to 300
    thumb_shape = "square", #Optional - Defaults to "circle"
    step = 1, #Optional - Defaults to 1
    default_value= default_value ,#Optional - Defaults to 0
    min_value= 0, # Defaults to 0
    max_value= max_value, # Defaults to 10
    track_color = "blue", #Optional - Defaults to Streamlit Red
    slider_color = ('red','blue'), #Optional
    thumb_color= "orange", #Optional - Defaults to Streamlit Red
    value_always_visible = True ,#Optional - Defaults to False
)

with col3:  
    vertical_slider(
    label = "Needs",  #Optional
    key = "vert_03" ,
    height = 300, #Optional - Defaults to 300
    thumb_shape = "square", #Optional - Defaults to "circle"
    step = 1, #Optional - Defaults to 1
    default_value= default_value ,#Optional - Defaults to 0
    min_value= 0, # Defaults to 0
    max_value= max_value, # Defaults to 10
    track_color = "blue", #Optional - Defaults to Streamlit Red
    slider_color = ('red','blue'), #Optional
    thumb_color= "orange", #Optional - Defaults to Streamlit Red
    value_always_visible = True ,#Optional - Defaults to False
)

with col4:  
    vertical_slider(
    label = "Engagement",  #Optional
    key = "vert_04" ,
    height = 300, #Optional - Defaults to 300
    thumb_shape = "square", #Optional - Defaults to "circle"
    step = 1, #Optional - Defaults to 1
    default_value= default_value ,#Optional - Defaults to 0
    min_value= 0, # Defaults to 0
    max_value= max_value, # Defaults to 10
    track_color = "blue", #Optional - Defaults to Streamlit Red
    slider_color = ('red','blue'), #Optional
    thumb_color= "orange", #Optional - Defaults to Streamlit Red
    value_always_visible = True ,#Optional - Defaults to False
)

equity_calculator = EquityCalculator(data="NCQG Data.xlsx")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🥇Ranking Table", "📊 Comparison to current flows", "🎛️ Regional Distribution", 
"🗺️ Map", "ℹ️ About"])
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