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

if 'analysis_data_type' not in st.session_state:
    st.session_state.analysis_data_type = None


if 'analyze_airbnp_data' not in st.session_state:
    st.session_state.analyze_airbnp_data = None


room_type = None
property_type = None

#@st.cache_data(ttl=100*1000, experimental_allow_widgets=True)
def show_home_screen():
    if os.path.exists(csv_file) == False:
        st.title ("AIRBNB ANALYSIS")
        show_upload_file_option()
    else:
        col1, col2 = st.columns([2,1])
        with col1:
            st.title ("AIRBNB ANALYSIS")
        with col2:
            st.write("")
            st.write("")
            if os.path.exists(csv_file) == True:
                if st.button(label="Delete Data", 
                        type="primary"):
                    delete_stored_data(csv_file)
        
        st.write("")
        st.write("")
        if os.path.exists(csv_file) == True:
            st.write(read_csv_data())
        else:
            show_upload_file_option()


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


def show_descriptive_data_view(data_field):
    
    c1,c2 = st.columns([2, 4])
    with c1:
        determine_data = st.session_state.analyze_airbnp_data[data_field].describe()
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

                    if(data_field == "Availability_30" or data_field == "Availability_60" or 
                    data_field == "Availability_90" or data_field == "Availability_365"):
                        st.session_state.analysis_data_type = "Availability"
                    elif(data_field == "Host_name"):
                        st.session_state.analysis_data_type = "Host"
                    elif data_field == "Room_type":
                        st.session_state.analysis_data_type = "Room Type"
                    elif data_field == "Price":
                        st.session_state.analysis_data_type = "Price"
                    else:
                        st.session_state.analysis_data_type = None

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
                col5.metric(label="Total Host Neighbourhood", value=f'{len(st.session_state.analyze_airbnp_data.host_neighborhood.unique())}',delta=int(len(st.session_state.analyze_airbnp_data.host_neighborhood.unique())/10))

                    
            
        if(data_field != "Not selected"):


            parent1 = st
            if(st.session_state.analysis_data_type != None):
                descrtiptive, analysis = st.tabs(["Descriptive Statistics & Data  Distribution", f"{st.session_state.analysis_data_type} Data Analysis"])
                parent1 = descrtiptive

            with parent1.container(border=True):
                c1, c2 = st.columns([17, 2])
                c1.markdown( f"<h2 style='font-size: 30px;'><span style='color: cyan;'>Descriptive Statistics</span> <span style='color: white;'> & </span><span style='color: cyan;'> Data  Distribution</span></h2>",unsafe_allow_html=True)
                c2.write("")
                show_descriptive_data_view(data_field)
 

                

            ## Data analysis
            if st.session_state.analysis_data_type != None:
                with analysis.container(border=True):
                    c1, c2 = st.columns([17, 2])
                    c1.markdown( f"<h2 style='font-size: 30px;'><span style='color: cyan;'> {st.session_state.analysis_data_type}</span> <span style='color: white;'>Data Analysis</span></h2>",unsafe_allow_html=True)
                    
                    c2.write("")
                    show_data_analysis(st.session_state.analysis_data_type)



                

def show_data_analysis(type):
    if(type == "Availability"):
        show_availability_analysis()
    elif(type == "Host"):
        show_host_data_analysis()
    elif type == "Room Type":
        show_room_type_data_analysis()
    elif type == "Price":
        show_price_data_analysis()

def show_price_data_analysis():
    col1,col2 = st.columns([5,5])
    list = []

    field_type = col1.selectbox('Choose data field', ['Host_name',"host_neighborhood","Property_type","Room_type"])
    option = col2.selectbox(f'Choose option', ["Maximum", "Minimum"])

    st.markdown( f"<h1 style='font-size: 20px;'><span style='color: cyan;'> Top 10 {option} </span><span style='color: white;'> {field_type}  based on </span> <span style='color: cyan;'> Price </span></h1>",unsafe_allow_html=True)


    if option == "Maximum":
        host_filter = st.session_state.analyze_airbnp_data.groupby(f'{field_type}')['Price'].sum().nlargest(10)
        name = host_filter.index.tolist()
        value = host_filter.values.tolist()
        fig = px.bar( x=name, y=value)
        fig.update_layout(title_x=1)
        fig.update_layout(
            plot_bgcolor='#0E1117',
            paper_bgcolor='#0E1117',
            xaxis_title_font=dict(color='#0DF0D4'),
            yaxis_title_font=dict(color='#0DF0D4')
        )
        fig.update_traces(hoverlabel=dict(bgcolor="#0E1117"),
                            hoverlabel_font_color="#0DF0D4")
        fig.update_xaxes(title_text="Host Name")
        fig.update_yaxes(title_text="Price")
        fig.update_traces(marker_color='#1BD4BD')
        st.plotly_chart(fig, theme=None, use_container_width=True)

    if option == "Minimum":
        host_filter = st.session_state.analyze_airbnp_data.groupby(f'{field_type}')['Price'].sum().nsmallest(10)
        name = host_filter.index.tolist()
        value = host_filter.values.tolist()
        fig = px.bar( x=name, y=value)
        fig.update_layout(title_x=1)
        fig.update_layout(
            plot_bgcolor='#0E1117',
            paper_bgcolor='#0E1117',
            xaxis_title_font=dict(color='#0DF0D4'),
            yaxis_title_font=dict(color='#0DF0D4')
        )
        fig.update_traces(hoverlabel=dict(bgcolor="#0E1117"),
                            hoverlabel_font_color="#0DF0D4")
        fig.update_xaxes(title_text="Host Name")
        fig.update_yaxes(title_text="Price")

        fig.update_traces(marker_color='#1BD4BD')
        
        st.plotly_chart(fig, theme=None, use_container_width=True)


def show_room_type_data_analysis():
    col1,col2 = st.columns([5,5])
    list = []

    room_type = col1.selectbox('Choose Room Type', st.session_state.analyze_airbnp_data["Room_type"].unique())
    option = col2.selectbox(f'Choose option', ["Maximum", "Minimum"])

    if option == 'Minimum':
        st.markdown( f"<h1 style='font-size: 20px;'><span style='color: cyan;'> Top 10  </span><span style='color: white;'> minimun price host neighbourhoods based on Room Type :</span> <span style='color: cyan;'> {room_type}</span></h1>",unsafe_allow_html=True)
        filter = st.session_state.analyze_airbnp_data.query(f"Room_type== '{room_type}'").groupby('host_neighborhood')['Price'].mean().nsmallest(10)

        name = filter.index.tolist()

        value = filter.values.tolist()
        fig = px.bar( x=name, y=value)
        fig.update_layout(title_x=1)
        fig.update_layout(
            plot_bgcolor='#0E1117',
            paper_bgcolor='#0E1117',
            xaxis_title_font=dict(color='#0DF0D4'),
            yaxis_title_font=dict(color='#0DF0D4')
        )
        fig.update_traces(hoverlabel=dict(bgcolor="#0E1117"),
                            hoverlabel_font_color="#0DF0D4")
        fig.update_xaxes(title_text="Host Name")
        fig.update_yaxes(title_text="Listings Count")
        fig.update_traces(marker_color='#1BD4BD')
        st.plotly_chart(fig, theme=None, use_container_width=True)

        # min reviews rank based on room type
        st.markdown( f"<h1 style='font-size: 20px;'><span style='color: cyan;'> Top 10  </span><span style='color: white;'> minimum review host neighbourhoods based on Room Type :</span> <span style='color: cyan;'> {room_type}</span></h1>",unsafe_allow_html=True)
        filter = st.session_state.analyze_airbnp_data.query(f"Room_type== '{room_type}'").groupby('host_neighborhood')['Num_of_reviews'].sum().nsmallest(10)

        name = filter.index.tolist()

        value = filter.values.tolist()
        fig = px.bar( x=name, y=value)
        fig.update_layout(title_x=1)
        fig.update_layout(
            plot_bgcolor='#0E1117',
            paper_bgcolor='#0E1117',
            xaxis_title_font=dict(color='#0DF0D4'),
            yaxis_title_font=dict(color='#0DF0D4')
        )
        fig.update_traces(hoverlabel=dict(bgcolor="#0E1117"),
                            hoverlabel_font_color="#0DF0D4")
        fig.update_xaxes(title_text="Host Name")
        fig.update_yaxes(title_text="Review Count")
        fig.update_traces(marker_color='#1BD4BD')
        st.plotly_chart(fig, theme=None, use_container_width=True)

        

    elif option == 'Maximum':
        st.markdown( f"<h1 style='font-size: 20px;'><span style='color: cyan;'> Top 10  </span><span style='color: white;'> Maximun price host neighbourhoods based on Room Type :</span> <span style='color: cyan;'> {room_type}</span></h1>",unsafe_allow_html=True)
        filter = st.session_state.analyze_airbnp_data.query(f"Room_type== '{room_type}'").groupby('host_neighborhood')['Price'].mean().nlargest(10)

        name = filter.index.tolist()

        value = filter.values.tolist()
        fig = px.bar( x=name, y=value)
        fig.update_layout(title_x=1)
        fig.update_layout(
            plot_bgcolor='#0E1117',
            paper_bgcolor='#0E1117',
            xaxis_title_font=dict(color='#0DF0D4'),
            yaxis_title_font=dict(color='#0DF0D4')
        )
        fig.update_traces(hoverlabel=dict(bgcolor="#0E1117"),
                            hoverlabel_font_color="#0DF0D4")
        fig.update_xaxes(title_text="Host Name")
        fig.update_yaxes(title_text="Listings Count")
        fig.update_traces(marker_color='#1BD4BD')
        st.plotly_chart(fig, theme=None, use_container_width=True)

        # max reviews rank based on room type
        st.markdown( f"<h1 style='font-size: 20px;'><span style='color: cyan;'> Top 10  </span><span style='color: white;'> maximun review host neighbourhoods based on Room Type :</span> <span style='color: cyan;'> {room_type}</span></h1>",unsafe_allow_html=True)
        filter = st.session_state.analyze_airbnp_data.query(f"Room_type== '{room_type}'").groupby('host_neighborhood')['Num_of_reviews'].sum().nlargest(10)

        name = filter.index.tolist()

        value = filter.values.tolist()
        fig = px.bar( x=name, y=value)
        fig.update_layout(title_x=1)
        fig.update_layout(
            plot_bgcolor='#0E1117',
            paper_bgcolor='#0E1117',
            xaxis_title_font=dict(color='#0DF0D4'),
            yaxis_title_font=dict(color='#0DF0D4')
        )
        fig.update_traces(hoverlabel=dict(bgcolor="#0E1117"),
                            hoverlabel_font_color="#0DF0D4")
        fig.update_xaxes(title_text="Host Name")
        fig.update_yaxes(title_text="Review Count")
        fig.update_traces(marker_color='#1BD4BD')
        st.plotly_chart(fig, theme=None, use_container_width=True)

            
                


def show_host_data_analysis():
    col1,col2 = st.columns([5,5])
    list = []

    type = col1.selectbox('Choose Filter', ["Neighborhood", "Room type"])
    if(type == "Neighborhood"):
        list = st.session_state.analyze_airbnp_data["host_neighborhood"].unique()
    elif(type == "Room type"):
        list = st.session_state.analyze_airbnp_data.Room_type.unique()
            
    sel_data = col2.selectbox(f'Choose {type}', list)

    if(type == "Neighborhood"):
        show_host_neighborhood_data(sel_data)    
    elif type == "Room type":
        show_host_room_type_data(sel_data)   




def show_host_room_type_data(room_type):
    st.markdown( f"<h1 style='font-size: 20px;'><span style='color: cyan;'> Top  10  Hosts</span><span style='color: white;'>  based on </span> <span style='color: green;'> Room Type : {room_type} </span></h1>",unsafe_allow_html=True)

    filter = st.session_state.analyze_airbnp_data.query(f"Room_type=='{room_type}'").groupby('Host_name')['host_total_listings_count'].sum().nlargest(10)
    name = filter.index.tolist()
    value = filter.values.tolist()
    fig = px.bar( x=name, y=value)
    fig.update_layout(title_x=1)
    fig.update_layout(
        plot_bgcolor='#0E1117',
        paper_bgcolor='#0E1117',
        xaxis_title_font=dict(color='#0DF0D4'),
        yaxis_title_font=dict(color='#0DF0D4')
    )
    fig.update_traces(hoverlabel=dict(bgcolor="#0E1117"),
                        hoverlabel_font_color="#0DF0D4")
    fig.update_xaxes(title_text="Host Name")
    fig.update_yaxes(title_text="Listings Count")
    fig.update_traces(marker_color='#1BD4BD')
    st.plotly_chart(fig, theme=None, use_container_width=True)

            
def show_host_neighborhood_data(neighbor_data):
    try:
        if(isinstance(neighbor_data, str) == False):
            neighbor_data = ""
        elif(neighbor_data.strip() == "nan"):
            neighbor_data = ""

        st.markdown( f"<h1 style='font-size: 20px;'><span style='color: cyan;'> Top  10  Hosts </span><span style='color: white;'>  based on </span> <span style='color: green;'> Host Neighbourhood : {neighbor_data} </span></h1>",unsafe_allow_html=True)

        filter = st.session_state.analyze_airbnp_data.query(f"host_neighborhood=='{neighbor_data}'").groupby('Host_name')['host_total_listings_count'].sum().nlargest(10)

        name = filter.index.tolist()
        value = filter.values.tolist()
        fig = px.bar( x=name, y=value)
        fig.update_layout(title_x=1)
        fig.update_layout(
            plot_bgcolor='#0E1117',
            paper_bgcolor='#0E1117',
            xaxis_title_font=dict(color='#0DF0D4'),
            yaxis_title_font=dict(color='#0DF0D4')
        )
        fig.update_traces(hoverlabel=dict(bgcolor="#0E1117"),
                            hoverlabel_font_color="#0DF0D4")
        fig.update_xaxes(title_text="Host Name")

        fig.update_yaxes(title_text="Listings Count")

        fig.update_traces(marker_color='#1BD4BD')
        
        st.plotly_chart(fig, theme=None, use_container_width=True)
    except Exception as Err:
        st.write("Data not available")


def show_availability_analysis():
    # Filters :
    col1,col2 = st.columns([5,5])
    room_type = col1.selectbox('Choose Room Type', st.session_state.analyze_airbnp_data.Room_type.unique())
    property_type = col2.selectbox('Choose Property Type', st.session_state.analyze_airbnp_data.Property_type.unique())
    
    st.markdown( f"<h1 style='font-size: 20px;'><span style='color: cyan;'> Availability  days </span><span style='color: white;'>  based on</span> <span style='color: green;'> {room_type} </span> <span style='color: white;'> and</span> <span style='color: red;'> {property_type}</span></h1>",unsafe_allow_html=True)

    value = st.session_state.analyze_airbnp_data.query(f"Room_type=='{room_type}' and Property_type == '{property_type}'")[['Availability_30', 'Availability_60', 'Availability_90', 'Availability_365']].sum()
    name=['Availability_30','Availability_60','Availability_90','Availability_365']

    fig = px.bar( x=name, y=value)
    fig.update_layout(title_x=1)
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
    st.title("PowerBi Data Evaluation")
    if st.button("Open PowerBi Dashboard", type="primary"):
        url= 'https://app.powerbi.com/groups/me/reports/f19c50ea-6e0e-42cc-a0b7-a87f1af11294/a04dfc4748479f39a448?experience=power-bi'  
        # Open the URL using open() function of module  
        webbrowser.open_new_tab(url)  

# page configuraton
st.set_page_config (layout="wide", page_title="AirBnB Analysis")

with st.sidebar:
    select = option_menu("airbnb", ["Home","Data Analysis","Power BI"])

if select == "Home":
    show_home_screen()
    pass
elif select == "Data Analysis":
    show_data_visualzation_screen()
    pass
elif select == "Power BI":
    show_powerbi_page()
    pass



