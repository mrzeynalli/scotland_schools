# import necessary librarues
import json, folium
import pandas as pd
from postcodes_api import PostcodeApi
import os


### LOADING AND PROCESSING THE DATASETS


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


### USING POSTCODES API TO CALL SCHOOL LOCATIONS

# create a dictionary to store the collected data
sch_loc_info = {'locs' : [], 'cities' : [], 'zones' : []}


# NOTE: When sending bulk postcodes, the API gate can only take 100 at a time. So, we request info 100 by 100
for i in range(100,len(postcodes),100):

    sch_loc_info_100 = PostcodeApi().get_bulk_pos_info(postcodes[i-100:i]) # request the info for each 100 call
    sch_loc_info['locs'] += sch_loc_info_100['locs'] # store the location info
    sch_loc_info['cities'] +=  sch_loc_info_100['cities'] # store the citiyes
    sch_loc_info['zones'] += sch_loc_info_100['zones'] # store the zones

    if (len(postcodes) - i) < 100: # include the final call which would have less than 100 postcodes.
        sch_loc_info_less = PostcodeApi().get_bulk_pos_info(postcodes[i:len(postcodes)])
        
        sch_loc_info['locs'] += sch_loc_info_less['locs']
        sch_loc_info['cities'] +=  sch_loc_info_less['cities']
        sch_loc_info['zones'] += sch_loc_info_less['zones']

# concatenate the schools dataframe and the geo-location information dataframe
sch_df = pd.concat([pd.DataFrame(sch_jsn), pd.DataFrame(sch_loc_info)], axis=1)

# drop null values: bear in mind that some postcodes did not recevie information because of being terminated
sch_df.dropna(inplace=True)


### CREATE AND SAVE THE MAP

# Create a map centered at Edinburgh, the capital of Scotland
m = folium.Map(location=[55.941457, -3.205744], zoom_start=6.5)

# Create a custom color scale from light to dark blue
colors = {
    1: '#08306b',  # Dark blue (most deprived)
    2: '#08519c',
    3: '#3182bd',
    4: '#63b7f4',
    5: '#a6e1fa'   # Light blue (least deprived)
}

# length of the schools
l = len(sch_df)

# Create circles and digits for each data point
for i in range(l):

    school = sch_df['School Name_x'].iloc[i] # school name
    pos = sch_df['Post Code'].iloc[i] # postcode
    loc = sch_df['locs'].iloc[i] # location
    city = sch_df['cities'].iloc[i] # city
    zone = sch_df['zones'].iloc[i] # zone
    pupils = sch_df['Total pupils'].iloc[i] # total pupils
    type = sch_df['School Type'].iloc[i] # type of the school: secondary, primary, or special

    mag = dep_rates.get(pos, 3) # get the deprivation score as magnitutde; 3 if the postcode is not assigned a score

    # add circle markers pointing each school
    folium.CircleMarker(
        location=loc,
        radius=(pupils/100 if pupils != 0 else 1), # radius equivalent to the total pupils count in each school
        color=colors[mag],
        fill=True,
        fill_opacity=0.8,
    ).add_to(m)
    
    # create an HTML pop-up for each school
    popup_html = f"""
    <h3>{school}</h3>
    <p><strong>Type:</strong> {type}</p>
    <p><strong>Local Authority:</strong> {city}</p>
    <p><strong>Zone:</strong> {zone}</p>
    <p><strong>Pupils:</strong> {pupils if pupils != 0 else 'N/A'}</p>
    <p><strong>Deprivation:</strong> {mag}</p>"""

    folium.Marker(
        location=loc,
        popup=folium.Popup(popup_html, max_width=150),
        icon=folium.DivIcon(html=f'<div style="width: 0px; height: 0px;"></div>'),
    ).add_to(m)

# Create a custom HTML legend
legend_html = """
<div style="position: fixed; top: 10px; right: 10px; background-color: white; padding: 10px; border: 2px solid black; z-index: 1000;">
    <p><strong>Legend</strong></p>
    <p><span style="color: black;"><span style="background-color: #08306b; width: 20px; height: 20px; display: inline-block;"></span> 1 - Most Deprived</span></p>
    <p><span style="color: black;"><span style="background-color: #08519c; width: 20px; height: 20px; display: inline-block;"></span> 2</span></p>
    <p><span style="color: black;"><span style="background-color: #3182bd; width: 20px; height: 20px; display: inline-block;"></span> 3</span></p>
    <p><span style="color: black;"><span style="background-color: #63b7f4; width: 20px; height: 20px; display: inline-block;"></span> 4</span></p>
    <p><span style="color: black;"><span style="background-color: #a6e1fa; width: 20px; height: 20px; display: inline-block;"></span> 5 - Least Deprived</span></p>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))


# Create the folder to save the map
cwd = os.getcwd()
folder = os.path.join(cwd,'map')

os.makedirs(folder, exist_ok=True)
# save the map as an HTML file
m.save(os.path.join(folder, 'scottish_schools_map.html'))