import streamlit as st
from pandas import DataFrame
import pandas as pd
from elasticsearch import Elasticsearch
from pandas.io.json import json_normalize
from streamlit_folium import folium_static
import folium
import datetime as datetime
import os
from dotenv import load_dotenv


# define a function (for later use)
def epoch_to_datetime(epoch_time):
    try:
        # Convert epoch time to datetime object
        dt = datetime.datetime.fromtimestamp(epoch_time/1000000).strftime("%Y/%m/%d")
        return dt
    except OSError:
        # If an error occurs during conversion, return default date
        return datetime.date(1970, 1, 1)


# connect to Elasticsearch
load_dotenv()
os.environ['CUDA_VISIBLE_DEVICES'] = os.getenv('CUDA_VISIBLE_DEVICES')
ELASTIC_USER = os.getenv('ELASTIC_USER')
ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD')

es = Elasticsearch(["http://localhost:9200"], basic_auth=(os.getenv('ELASTIC_USER'), 
                                                         os.getenv('ELASTIC_PASSWORD')))

st.set_page_config(layout="wide")

# Add title to sidebar
st.sidebar.title('San Francisco App Scan Tracker')

################ Search by free text

text = st.sidebar.text_input("Free Text Search", placeholder='example: burger')
if text:

    #build the search query that searches everything
    query_body = {
        "query": {
            "simple_query_string" : {
                "query": text       ## example of free text: burger
            }
        }
    }

    
    res = es.search(index="contract_tracing", body=query_body , size=1000)  # search the index   
    df = pd.json_normalize(res['hits']['hits'])     # extract the data needed


    # scenario if query search have data result
    if len(df) > 0:
        df = df.drop_duplicates(subset=['_source.business_id'])     # drop the duplicates

        # rename the lang lot columns so they have the right name for the map function
        df = df.rename(columns={"_source.latitude": "latitude", "_source.longitude": "longitude"})
        df = df.filter(items = ['_source.business_id','_source.business_name','_source.business_address','latitude','longitude','_source.zip'], axis = 1)

        # Add the table with a headline
        st.header(f"Businesses for search: {text}")

        # show the data as table
        table_df = df.filter(items = ['_source.business_id','_source.business_name','_source.business_address','_source.zip'], axis = 1)
        
        # fix names before printing the table
        table_df = table_df.rename(columns={"_source.business_id": "Business ID", "_source.business_name": "Name", "_source.business_address": "Address", "_source.zip": "Postal Code"})
        
        # print the table
        table1 = st.dataframe(data=table_df)
        
        # this will print the boring standard app from streamlit
        #st.map(data=df, zoom=None, use_container_width=True)

        # visualize the Folium Map
        map = folium.Map(location=[df.iloc[0]['latitude'], df.iloc[0]['longitude']], zoom_start=10)

        for index, row in df.iterrows():
            folium.Marker(
                [row['latitude'], row['longitude']], popup=f"{row['_source.business_name']} <br> ID= {row['_source.business_id']}", tooltip=row['_source.business_name']).add_to(map)

        folium_static(map, height=600, width=900)

    # scenario if query search have no data result
    else:
        error_message = "An error occurred: {}".format("<br/>The query have no result.<br/> Please try other keywords.")
        error_message_style = '<span style="color: red; font-weight: bold;">{}</span>'.format(error_message)
        st.write(error_message_style, unsafe_allow_html=True)


################ Search by postal code

# add the input field for postal code
postal_code = st.sidebar.text_input("Zip Code", placeholder="example: 94129")

# add the link to the Atlanta map below the code
link = "[All San Francisco Zip codes](https://www.usmapguide.com/california/san-francisco-zip-code-map/)"
st.sidebar.markdown(link, unsafe_allow_html=False) 

# add a separator 
myseparator = "---"
st.sidebar.markdown(myseparator, unsafe_allow_html=False) 

# search for postal code
if postal_code:

     #build the search query
    query_body = {
    "query": {
        "match": {
            "zip": postal_code      ## example of postal code: 94129
            } 
        } 
    }

    res = es.search(index="contract_tracing", body=query_body , size=1000)

    # get the results and put them into a dataframe
    df = pd.json_normalize(res['hits']['hits'])

    if len(df) > 0:
        # drop the duplicates
        df = df.drop_duplicates(subset=['_source.business_id'])

        # rename the lang lot columns so they have the right name for the map function
        df = df.rename(columns={"_source.latitude": "latitude", "_source.longitude": "longitude"})
        
        df = df.filter(items = ['_source.business_id','_source.business_name','_source.business_address','latitude','longitude','_source.zip'], axis = 1)
        
        # Add the table with a headline
        st.header("Businesses in Postal code")
        # show the data as table
        
        table_df = df.filter(items = ['_source.business_id','_source.business_name','_source.business_address','_source.zip'], axis = 1)
        
        # fix names before printing the table
        table_df = table_df.rename(columns={"_source.business_id": "Business ID", "_source.business_name": "Name", "_source.business_address": "Address", "_source.zip": "Postal Code"})
        
        # print the table
        table2 = st.dataframe(data=table_df)
        
        # this will print the boring standard app from streamlit
        #st.map(data=dkf, zoom=None, use_container_width=True)

        # print a folium map. Really cool
        m = folium.Map(location=[df.iloc[0]['latitude'], df.iloc[0]['longitude']], zoom_start=13)
        
        # add the markers
        for index, row in df.iterrows():
            folium.Marker(
                [row['latitude'], row['longitude']], popup=f"{row['_source.business_name']} <br> ID= {row['_source.business_id']}", tooltip=row['_source.business_name']).add_to(m)

        folium_static(m, height=600, width=900)

    else:
        error_message = "An error occurred: {}".format("<br/>The query have no result.<br/> Please try other keywords.")
        error_message_style = '<span style="color: red; font-weight: bold;">{}</span>'.format(error_message)
        st.write(error_message_style, unsafe_allow_html=True)


################ Search by Business ID

# create the input field on the sidebar    
business_id = st.sidebar.text_input("Business ID", placeholder="example: 0430533-01-001")

if business_id:
    #build the search query for Elasticsearch
    query_body = {
        "query":{
            "simple_query_string":{
                "query":business_id,  ## example business ID: 0430533-01-001
                "fields": ["business_id"],
                "default_operator":"AND"
            }
        }
    }

    
    res = es.search(index="contract_tracing", body=query_body ,size=10000)  # search the index
    
    # get the results and put them into a dataframe
    df = pd.json_normalize(res['hits']['hits'])
    
    if len(df) > 0:
        table_df = df.filter(items = ['_source.scan_timestamp','_source.deviceID','_source.user_name','_source.user_birth_date'], axis = 1)
        
        # turn the epochs into timestamps
        # table_df['_source.user_birth_date'] = table_df['_source.user_birth_date'].apply(lambda s: datetime.datetime.fromtimestamp(s/1000000).strftime("%Y/%m/%d"))
        # table_df['_source.scan_timestamp'] = table_df['_source.scan_timestamp'].apply(lambda s: datetime.datetime.fromtimestamp(s/1000000).strftime("%Y/%m/%d %H:%M:%S"))

        table_df['_source.user_birth_date'] = table_df['_source.user_birth_date'].apply(lambda s: epoch_to_datetime(s))
        table_df['_source.scan_timestamp'] = table_df['_source.scan_timestamp'].apply(lambda s: epoch_to_datetime(s))

        # sort values by timestamp
        table_df = table_df.sort_values(by=['_source.scan_timestamp'])
        
        # fix names before printing the table
        table_df = table_df.rename(columns={"_source.scan_timestamp": "Scan Timestamp","_source.deviceID": "Device ID", "_source.user_name": "User Name", "_source.user_birth_date": "Birth Date"})

        # add a header before the table
        st.header(f"Users scanned at this business: {business_id}")
        
        # print the table
        table3 = st.dataframe(data=table_df)

    else:
        error_message = "An error occurred: {}".format("<br/>The query have no result.<br/> Please try other keywords.")
        error_message_style = '<span style="color: red; font-weight: bold;">{}</span>'.format(error_message)
        st.write(error_message_style, unsafe_allow_html=True)

################ Search by Device ID

# Below the fist chart add a input field for the invoice number
device_id = st.sidebar.text_input("Device ID", placeholder="example: 8243260197590")
#st.text(inv_no)  # Use this to print out the content of the input field

# if enter has been used on the input field 
if device_id:
    #build the search query for Elasticsearch
    query_body = {
    "query": {
        "match": {
            "deviceID": device_id       ## example of device ID: 8243260197590
            } 
        } 
    }

    res = es.search(index="contract_tracing", body=query_body ,size=1000)  # search the index
    
    # get the results and put them into a dataframe
    df = pd.json_normalize(res['hits']['hits'])

    if len(df) > 0:
        # rename the lang lot columns so they have the right name for the map function
        df = df.rename(columns={"_source.latitude": "latitude", "_source.longitude": "longitude"})
        
        # Add the table with a headline
        st.header(f"User scans for user: {device_id}")
        
        # Turn the epoch into timestamp
        df['_source.scan_timestamp'] = df['_source.scan_timestamp'].apply(lambda s: datetime.datetime.fromtimestamp(s/1000000).strftime("%Y/%m/%d %H:%M:%S"))  
        
        # filter only the needed colums
        table_df = df.filter(items = ['_source.scan_timestamp','_source.business_id','_source.business_name','_source.business_address','longitude','latitude'], axis = 1)  #,'latitude','longitude'
        
        # sort the visited places by timestamp
        table_df = table_df.sort_values('_source.scan_timestamp', axis = 0)

        # fix names before printing the table
        table_df = table_df.rename(columns={"_source.scan_timestamp": "Scan Timestamp","_source.business_id": "Business ID", "_source.business_name": "Business Name", "_source.business_address": "Business Address"})

        # print the table
        table4 = st.dataframe(data=table_df) 

        # add the folium maps
        m = folium.Map(location=[df.iloc[0]['latitude'], df.iloc[0]['longitude']], zoom_start=10)
        
        for index, row in df.iterrows():
            folium.Marker(
                [row['latitude'], row['longitude']], popup=row['_source.scan_timestamp'], tooltip=row['_source.business_name']
            ).add_to(m)

        # print the map
        folium_static(m, height=600, width=900)

    else:
        error_message = "An error occurred: {}".format("<br/>The query have no result.<br/> Please try other keywords.")
        error_message_style = '<span style="color: red; font-weight: bold;">{}</span>'.format(error_message)
        st.write(error_message_style, unsafe_allow_html=True)
