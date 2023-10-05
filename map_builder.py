# import necessary librarues
import json, folium
import pandas as pd
from postcodes_api import PostcodeApi

# load the school data
sch_stat = pd.read_excel('Datasets/scottish_schools_stats.xlsx') # school stats
sch_info = pd.read_excel('Datasets/scottish_schools_contact.xlsx', sheet_name='Open Schools') # school contact info
dep = pd.read_excel('Datasets/postcode_deprivation.xlsx') # deprivation scores for each postcode


# convert deprivation scores into a dictionary to be called easily
dep_rates = {}

for p,d in dep.values:
    dep_rates[p] = d


# rename 'Seed Code' column name into 'SeedCode' to be merged with the school stats dataset
sch_info = sch_info.rename(columns={'Seed Code' : 'SeedCode'})

# merge school stats and contact info datasets
sch_df = sch_info.merge(sch_stat, on='SeedCode', how='right')

# drop the null values
sch_df.dropna(inplace=True)

# convert the final df into a dictionary using JSON
sch_jsn = json.loads(sch_df.to_json(orient='records'))

# store all the school postcodes inside a list
postcodes = [sch['Post Code'] for sch in sch_jsn]

