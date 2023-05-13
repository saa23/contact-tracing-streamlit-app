import faker 
import pandas as pd
import numpy as np
from random import randrange
import datetime as datetime
from datetime import timedelta


# Create a fake dataset for 100k users with name, state, birth date and device_id
Faker = faker.Factory().create
fake = Faker()
n = 100000
faker_data = pd.DataFrame([[fake.name(), 
                           fake.state(),
                           fake.date_of_birth(minimum_age =18, maximum_age = 65),
                           fake.msisdn()
                           ] 
            for _ in range(n)],
            columns=['user_name', 'user_state' , 'user_birth_date', 'deviceID'])
faker_data['user_id'] = range(1, 1+len(faker_data)) # create a column user_id with ascending values
faker_data = faker_data.convert_dtypes()                # convert the data types to the right types
faker_data = faker_data.astype({'user_id': 'int64'})    # fix the user_id type
faker_data['user_birth_date'] = pd.to_datetime(faker_data['user_birth_date'])  # change the birth date to datetime


# read the businesses dataset (10k rows)
businesses = pd.read_json("./data/sf_businesses.json", lines=True)
df_repeated = pd.concat([businesses]*100, ignore_index=True)    # create (10.000 * 100) businesses --> 1M rows by concatinating the same dataset multiple times
df_repeated['user_id'] = np.random.randint(1,100000, df_repeated.shape[0]) # randint needs to be the same as the amount of users --> 100k


# Join the two dataframes of the faked users to the one of the businesses
df_repeated2 = df_repeated.merge(faker_data, on = "user_id", how='left')


def random_date():
    """
    This function will return a random datetime between two datetime objects.
    """

    start = datetime.datetime.strptime('2023-01-11 12:00 AM', '%Y-%m-%d %I:%M %p')
    end = datetime.datetime.strptime('2023-01-23 11:55 PM', '%Y-%m-%d %I:%M %p')
 
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)


# create a new column using a lambda
df_repeated2['scan_timestamp'] = df_repeated2['business_name'].apply(lambda s: random_date())
print(df_repeated2)

# drop the user_id. We don't need it anymore
df_repeated2 = df_repeated2.drop('user_id', axis=1)

print(df_repeated2.dtypes)

# print a line of the dataframe
print(df_repeated2.head(1).to_json())

# Save the result data
# df_repeated2.to_parquet('./data/sf_fakedataset.parquet.gzip', compression='gzip')    # write the result into a zipped parquet file
df_repeated2.to_json('./data/sf_fakedataset.json', lines=True, orient='records')    # sve into JSON format if we need it
