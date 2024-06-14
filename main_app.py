import streamlit as st
import json
from streamlit_option_menu import option_menu
from streamlit_extras.stylable_container import stylable_container
from main_functions import *
import plotly.express as px
import webbrowser  



# Create database
create_database()
create_database_and_table()

csv_file = "airbnb_data.csv"

# session state to maintain entered channel id
if 'show_data_reset_option' not in st.session_state:
    st.session_state.show_data_reset_option = False

if 'analyze_airbnp_data' not in st.session_state:
    st.session_state.analyze_airbnp_data = None


#@st.cache_data(ttl=100*1000, experimental_allow_widgets=True)
def show_home_screen():
    if st.session_state.show_data_reset_option == False:
        st.title ("AIRBNB ANALYSIS")
        show_upload_file_option()
    else:
        col1, col2 = st.columns([2,1])
        with col1:
            st.title ("AIRBNB ANALYSIS")
        with col2:
            st.write("")
            st.write("")
            if st.button(label="Restore Data", 
                    type="primary"):
                st.session_state.show_data_reset_option = False
        
        st.write("")
        st.write("")
        st.write(read_csv_data())

                
pass
               
                

def show_upload_file_option():
    uploaded_file = st.file_uploader("Drag & Drop or Select JSON file here to upload AirBnb data.", type=["json"])
        
    if st.button(label="Store the data into SQL & CSV", 
                type="primary", disabled= uploaded_file == None):
        if uploaded_file:
            with st.spinner("Saving the data into SQL & CSV..."):
                data = json.load(uploaded_file)
                df = insert_data_from_file(data)
                
                st.write(df)
                st.success("Done!")
            
                
        else:
            st.write("Unable to select file")
pass



def show_data_visualzation_screen():
    st.title ("Data Analysis")

    c1, c2 = st.columns([ 4,4])
    with c1:
        with st.container( border=True):
            #st.write("")
            data_source = st.selectbox(label= "Select Data Source", options=["Not selected", csv_data_source, sql_data_source])
            if(data_source != "Not selected"):
                st.session_state.analyze_airbnp_data = analyze_data(data_source)

                # data type selection
                data_type = st.selectbox(label= "Select Data Type", options=[continuous_data_type, categorical_data_type])
                if st.session_state.analyze_airbnp_data is not None:
                    columns_list = get_columns_by_type(analyze_airbnp_data= st.session_state.analyze_airbnp_data, data_type=data_type)
                    data_field = st.selectbox(label= "Select Data", options=columns_list)
            else:
                st.session_state.analyze_airbnp_data = None



    if st.session_state.analyze_airbnp_data is not None:
        st.session_state.analyze_airbnp_data['Id'] = st.session_state.analyze_airbnp_data['Id'].apply(lambda x : str(x))
        st.session_state.analyze_airbnp_data['Host_Id'] = st.session_state.analyze_airbnp_data['Host_Id'].apply(lambda x : str(x))
        
        with c2:
            with st.container(border = True):
                col1,col2,col3 = st.columns([10,10,10])

                col1.metric(label="Total Host Count", value=f'{len(st.session_state.analyze_airbnp_data.Host_name.unique())}',delta=int(len(st.session_state.analyze_airbnp_data.Host_name.unique())/100))
                col2.metric(label="Total Room Types", value=f'{len(st.session_state.analyze_airbnp_data.Room_type.unique())}',delta=int(len(st.session_state.analyze_airbnp_data.Room_type.unique())))
                col3.metric(label="Total Listings Available", value=f'{len(st.session_state.analyze_airbnp_data.Name.unique())}',delta=int(len(st.session_state.analyze_airbnp_data.Name.unique())/10))
                
                st.write("")
                st.write("")

                col4,col5 = st.columns([10,10])
                col4.metric(label="Total Amount Earned", value=f'{st.session_state.analyze_airbnp_data.Price.sum()}',delta=int(st.session_state.analyze_airbnp_data.Price.sum()/100))
                col5.metric(label="Total Host Neighbourhood", value=f'{len(st.session_state.analyze_airbnp_data.Neighborhood.unique())}',delta=int(len(st.session_state.analyze_airbnp_data.Neighborhood.unique())/10))

                    
            
        if(data_field != "Not selected"):
            st.markdown( f"<h2 style='font-size: 30px;'><span style='color: cyan;'> {data_field}</span> <span style='color: white;'>Data Analysis</span></h2>",unsafe_allow_html=True)

            determine_data = st.session_state.analyze_airbnp_data[data_field].describe()
            
            with st.expander(label=f"**Descriptive Statistics & Data  Distribution**"):

                c1,c2 = st.columns([2, 4])
                with c1:
                    st.write("Descriptive Statistics")
                    st.write(determine_data)
                with c2:
                    st.write("Data  Distribution")

                    fig = px.histogram(st.session_state.analyze_airbnp_data[f'{data_field}'], nbins=20)
                    fig.update_layout(
                        plot_bgcolor='#0E1117',
                        paper_bgcolor='#0E1117',
                        xaxis_title_font=dict(color='#0DF0D4'),
                        yaxis_title_font=dict(color='#0DF0D4')
                    )
                    fig.update_traces(hoverlabel=dict(bgcolor="#0E1117"),
                                        hoverlabel_font_color="#0DF0D4")
                    fig.update_xaxes(title_text="Availability Types")

                    fig.update_yaxes(title_text="Days  Count")

                    fig.update_traces(marker_color='#1BD4BD')
                    
                    st.plotly_chart(fig, theme=None, use_container_width=True)

            

def show_powerbi_page():
    url= 'https://app.powerbi.com/groups/me/reports/f19c50ea-6e0e-42cc-a0b7-a87f1af11294/a04dfc4748479f39a448?experience=power-bi'  
    # Open the URL using open() function of module  
    webbrowser.open_new_tab(url)  

# page configuraton
st.set_page_config (layout="wide", page_title="AirBnB Analysis")

with st.sidebar:
    select = option_menu("airbnb", ["Home","Data Analysis","Power BI"])

if select == "Home":
    st.session_state.show_data_reset_option = os.path.exists(csv_file)
    show_home_screen()
    pass
elif select == "Data Analysis":
    show_data_visualzation_screen()
    pass
elif select == "Power BI":
    pass#show_powerbi_screen()



