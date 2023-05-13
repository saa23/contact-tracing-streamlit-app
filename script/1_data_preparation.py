from ast import Lambda
from numpy import NaN
import pandas as pd
from pandas import DataFrame
import json
from sqlalchemy import true


def my_convert_json(value):
    try:
        return json.loads(value)
    except:
        return NaN


converter = {"Business Location": lambda x: x.replace("\'","\"")}           # create converter to replace ' to " so that Business Location will be valid json data format
in_df = pd.read_csv("./data/registered-business-locations-san-francisco-original.csv", converters = converter ) # read the csv using the converter
in_df['Business Location'] = in_df['Business Location'].map(lambda x: my_convert_json(x))                       # convert Business  Location to JSON format for later use
filtered_df = in_df[['Location Id', 'DBA Name','Street Address','City','Source Zipcode','Business Location']]   # filter only needed columns


cleaned_nonan_df = filtered_df.dropna().reset_index(drop=True)                                          # remove the NaNs
normalized = pd.json_normalize(cleaned_nonan_df['Business Location'], max_level=1)                      # Normalize the business location
longlat_df = pd.DataFrame(normalized['coordinates'].to_list(), columns = ['longitude', 'latitude'])     # create new df with longlat data
merged_df = pd.merge(cleaned_nonan_df, longlat_df, left_index=True, right_index=True)                   # merge again dataframe with long lat
filtered_df = merged_df[['Location Id', 'DBA Name','Street Address','City','Source Zipcode','latitude', 'longitude']]   # filter needed columns

sf_data = filtered_df.loc[filtered_df['City'] == 'San Francisco']   # filter only for SF locations
sf_data = sf_data.sample(n=10000)                                   # only use random sample 10k businesses (not all data)

ex_df = sf_data.rename(columns={
                        'Location Id': 'business_id', 
                        'DBA Name': 'business_name', 
                        'Street Address': 'business_address', 
                        'City': 'city',
                        'Source Zipcode': 'zip',
                        })

ex_df.to_json('./data/sf_businesses.json', lines=True, orient='records')  # save the output into a new json file (sf_businesses.json)
