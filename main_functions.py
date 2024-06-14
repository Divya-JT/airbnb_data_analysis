import json
import pandas as pd
import mysql.connector
import os

    
def create_database():
    try:   
        client = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "4444")
        cursor = client.cursor()
        
        # TO CREATE A DATABASE    
        query = "CREATE DATABASE IF NOT EXISTS airbnb_data"      
        cursor.execute(query)
    except Exception as error:
        print("Create DB error ", error)

# Sql Client with exist DB
def use_sql_client():
    client = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "4444",
        database = "airbnb_data"
    )
    return client

# create tables
def create_database_and_table():
    client = use_sql_client()
    cursor = client.cursor()
    
    # Create "Airbnb" main TABLE 
    query = """create table IF NOT EXISTS Airbnb(Id varchar(225) PRIMARY KEY, Name text , Description text, Neighborhood text, Property_type varchar(225), Room_type varchar(225),
            Min_night int, Max_night int, Accommodates int, Bedrooms int, Beds int, Num_of_reviews bigint,
            Bathrooms int, Price bigint , Host_Id varchar(225), Host_name varchar(225), lat varchar(225),
            lon varchar(225), Availability_30 int, Availability_60 int, Availability_90 int,
            Availability_365 int, review_scores_rating int, review_scores_value int, review_scores_communication int,
            review_scores_checkin int, review_scores_cleanliness int, review_scores_accuracy int)"""
    
    cursor.execute(query)

    # Create "room_amenities" TABLE 
    query = """create table IF NOT EXISTS room_amenities(ab_Id varchar(225) , Amenities text)"""
    cursor.execute(query)

    # Create "room_reviews" TABLE 
    query = """create table IF NOT EXISTS room_reviews(ab_Id varchar(225), review_id varchar(225), Reviewer_Id varchar(225), Rewiewer_name varchar(225), comments text)"""
    cursor.execute(query)

    
    # Create "room_reviews" TABLE 
    query = """create table IF NOT EXISTS data_insertion_status(status varchar(2))"""
    cursor.execute(query)

    client.close()



categorical_data_list = ["Name", "Description", "Neighborhood", "Property_type", 
                         "Room_type", "Host_name"]

continuous_data_list = ["Id", "Min_night", "Max_night", 
                        "Accommodates", "Bedrooms", "Beds", "Num_of_reviews",
                        "Bathrooms", "Price", "Host_Id", "lat",
                        "lon", "Availability_30", "Availability_60", "Availability_90",
                        "Availability_365", "review_scores_rating", "review_scores_value", 
                        "review_scores_communication", "review_scores_checkin", "review_scores_cleanliness", 
                        "review_scores_accuracy"]

# insert the loaded json data into DB
def insert_data_from_file(data):
    client = use_sql_client()
    cursor = client.cursor()


    columns = ["Id", "Name", "Description", "Neighborhood", "Property_type", "Room_type",
            "Min_night", "Max_night", "Accommodates", "Bedrooms", "Beds", "Num_of_reviews",
            "Bathrooms", "Price" , "Host_Id", "Host_name", "lat",
            "lon", "Availability_30", "Availability_60", "Availability_90",
            "Availability_365", "review_scores_rating", "review_scores_value", "review_scores_communication",
            "review_scores_checkin", "review_scores_cleanliness", "review_scores_accuracy", "Amenities"]

    data_frame_list = []
    main_values=[]
    main_query = """INSERT INTO Airbnb(Id, Name, Description, Neighborhood, Property_type, Room_type,
            Min_night, Max_night, Accommodates, Bedrooms, Beds, Num_of_reviews,
            Bathrooms, Price , Host_Id, Host_name, lat,
            lon, Availability_30, Availability_60, Availability_90,
            Availability_365, review_scores_rating, review_scores_value, review_scores_communication,
            review_scores_checkin, review_scores_cleanliness, review_scores_accuracy) 
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
    amenities_query = "INSERT INTO room_amenities(ab_Id, Amenities) VALUES(%s, %s)"
    review_query = "INSERT INTO room_reviews(ab_Id, review_id, Reviewer_Id, Rewiewer_name, comments) VALUES(%s, %s, %s, %s, %s)"

    amenities_values=[]
    review_values = []

    index = 0
    for  i in data:
        name = check_null_value(data=i, key="name", is_int=False)
        min_night = check_null_value(data=i, key="minimum_nights")
        beds = check_null_value(data=i, key="beds")
        bathrooms = check_null_value(data=i, key="bathrooms")
        review_scores_rating = check_null_value(data=i["review_scores"], key="review_scores_rating")
        review_scores_value = check_null_value(data=i["review_scores"], key="review_scores_value")
        review_scores_communication = check_null_value(data=i["review_scores"], key="review_scores_communication")
        review_scores_checkin = check_null_value(data=i["review_scores"], key="review_scores_checkin")
        review_scores_cleanliness = check_null_value(data=i["review_scores"], key="review_scores_cleanliness")
        review_scores_accuracy = check_null_value(data=i["review_scores"], key="review_scores_accuracy")

        row_data = (i ["_id"],
            name,
            i ["description"],
            i ["neighborhood_overview"],
            i ["property_type"],
            i ["room_type"],
            min_night, 
            i ["maximum_nights"],
            check_null_value(data = i, key ="accommodates"), 
            check_null_value(data = i, key ="bedrooms"), 
            beds, 
            i ["number_of_reviews"], 
            bathrooms,
            i ["price"],
            i ["host"] ["host_id"],
            i ["host"] ["host_name"],
            i ["address"] ["location"] ["coordinates"][0],
            i ["address"] ["location"] ["coordinates"][1],
            i ["availability"] ["availability_30"],
            i ["availability"] ["availability_60"],
            i ["availability"] ["availability_90"],
            i ["availability"] ["availability_365"],
            review_scores_rating,
            review_scores_value,
            review_scores_communication,
            review_scores_checkin,
            review_scores_cleanliness,
            review_scores_accuracy)
        main_values.append(
            row_data
        )



        row_data = row_data + ((','.join(i["amenities"])),)
        data_frame_list.append(row_data)
        

        for amenity in i["amenities"]:
            amenities_values.append((i["_id"], amenity))

        
        
        for review in i["reviews"]:
            review_values.append((i["_id"], review["_id"], check_null_value(data=review, key ="reviewer_id", is_int = True), 
                                  check_null_value(data=review, key ="reviewer_name", is_int = False), check_null_value(data=review, key ="comments", is_int = False)))
        
        


    # insert collected AirBnb data into SQL
    cursor.executemany(main_query, main_values)
    client.commit()

    # insert amenity into SQL
    cursor.executemany(amenities_query, amenities_values)       
    client.commit()

    # insert review data into SQL
    cursor.executemany(review_query, review_values)       
    client.commit()

    client.close()

    df = pd.DataFrame(data=data_frame_list, columns=columns)

    ## Save json data into CSV
    save_json_data_into_csv(df)
    change_data_insertion_status("1")

    return df

def save_json_data_into_csv(data_frame:pd.DataFrame):
    # convert json to data frame
    #df = pd.DataFrame.from_dict(data=pd.json_normalize(json_data), orient= "columns")

    # cleanup and pre processsing
    
    
    # convert data frame to csv file
    csv_file = "airbnb_data.csv"
    if(os.path.exists(csv_file)):
        os.remove(csv_file)
    
    csv_data = data_frame.to_csv(csv_file, index=True)

pass






def check_null_value(data, key, is_int = True):
    default_value = 0
    if is_int == True: 
        0 
    else: 
        ""
    
    if key in data:
        if data[key] is not None:
            default_value = data[key]
        
    return default_value

def change_data_insertion_status(status):
    try:
        client = use_sql_client()
        cursor = client.cursor()

        cursor.execute("DELETE FROM data_insertion_status;")
        client.commit()
        
        query = """INSERT INTO data_insertion_status (status) VALUES(%s)"""
        values = (status,)
        cursor.execute(query, values)
        client.commit()
        client.close()

    except Exception as err:
        print("change_data_insertion_status => Error : ", err)


def check_data_available_in_sql():
    status = "0"
    try:
        client = use_sql_client()
        cursor = client.cursor()
        
        cursor.execute("SELECT status FROM data_insertion_status;")

        myresult = cursor.fetchall()
        for result in myresult:
            status = result

        client.close()            
    except Exception as err:
        print("check_data_available_in_sql => Error : ", err)
        

    return status

def read_csv_data():
    return pd.read_csv("airbnb_data.csv")

csv_data_source = "CSV"
sql_data_source = "SQL"
categorical_data_type = "Categorical Data"
continuous_data_type = "Continuous Data"
def get_fields_by_data_type(data_source, data_type):
    if(data_source == csv_data_source):
        if(data_type == categorical_data_type):
            return categorical_data_list.__add__(["Amenities",])
        else:
            return continuous_data_list
        
    elif(data_source == sql_data_source):
        if(data_type == categorical_data_type):
            return categorical_data_list.__add__("Amenities")
        else:
            return continuous_data_list
        

def analyze_data(data_source):
    if data_source == csv_data_source:
        return read_csv_data()
    else:
        return pd.read_sql("SELECT * FROM airbnb_data.airbnb", use_sql_client())
    
def get_columns_by_type(analyze_airbnp_data, data_type):
    if(data_type == continuous_data_type):
        # Continuous data
        column_list = analyze_airbnp_data.select_dtypes(include=['int64','float64']).columns
        column_list.insert(0, "Not selected")
        return column_list
    else:
        # Categorical data
        column_list = analyze_airbnp_data.select_dtypes(include=['object']).columns
        column_list.insert(0, "Not selected")
        return column_list


# POWER BI
def show_powerbi_screen():
    pass
