"""
Publicly Available Electric Vehicle Charging Stations in the United States
Author: Amy K.
Date: June 2024

Objectives: Create
1) Static map of EV charging stations in the US, by facility type
2) Dynamic map of EV charging stations in the US, by charging availability during the hour of the day

Sources:
* National Renewable Energy Laboratory (June 2024)
    - https://developer.nrel.gov/docs/transportation/alt-fuel-stations-v1/
    - Requires an API key: https://developer.nrel.gov/signup/
* United States Census Bureau - Cartographic Boundary Files (2023)
    - https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html
"""

import os
import re
import requests
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import plotly.express as px
import contextily as ctx

######################
# SET UP

# request API key from user
API_KEY = input('Input your NREL API key:')

# set url + parameters for API request (publicly available EV charging stations)
ALT_FUEL_URL = 'https://developer.nrel.gov/api/alt-fuel-stations/v1.geojson?'
ALT_FUEL_PARAMETERS = f'api_key={API_KEY}&fuel_type=ELEC&status=E&access=public'

# set file paths
DIR = os.getcwd() + '/Documents/projects/2024-ev-charging-stations'
US_SHAPEFILE = DIR + '/data/cb_2023_us_county_500k/cb_2023_us_county_500k.shp'
OUTPUT_FOLDER = DIR + '/output/'

# define variables
DEFAULT_HOURS_START = '9am'  # assume charging stations are open at 9am by default
DEFAULT_HOURS_END = '5pm'  # assume charging stations close by 5pm by default

DF_COLS = [
    'id', 'open_date', 'facility_type', 'geometry',
    'station_name', 'street_address', 'city', 'state', 'zip',
    'groups_with_access_code', 'access_days_time']

MAP_COLS = {
    'NAME': 'name',
    'STUSPS': 'state',
    'STATE_NAME': 'state_name',
    'geometry': 'geometry'}

DROP_STATES = ['AK', 'HI',
               'VI', 'MP', 'GU', 'AS', 'PR',
               'AB', 'BC', 'MB', 'NB', 'NL', 'NS', 'NT', 'NU', 'ON', 'PE', 'SK', 'QC', 'YT']


# define functions
def categorize_facilities(value):
    if value in ['Factory']:
        return 'Industrial'
    elif value in ['Retail', 'Shopping Mall', 'Grocery', 'Shopping Center', 'Convenience Store',
                   'Pharmacy', 'Hardware Store', 'Bank', 'Brewery Distillery Winery',
                   'Travel Center', 'Restaurant',
                   'Fuel Reseller', 'Rental Car Return', 'Auto Repair', 'Carwash', 'Car Dealer']:
        return 'Retail'
    elif value in ['Workplace', 'Office Bldg']:
        return 'Office'
    elif value in ['Multi Unit Dwelling']:
        return 'Multi-Dwelling Unit'
    elif value in ['Hotel', 'Coop', 'B And B',  'Inn']:
        return 'Hotel / Lodging'
    elif value in ['School', 'College Campus']:
        return 'Education'
    elif value in ['Fed Gov', 'State Gov', 'Muni Gov',
                   'Motor Pool', 'Utility', 'Research Facility', 'Fire Station', 'Hospital']:
        return 'Government / Medical'
    elif value in ['Arena', 'Stadium', 'Museum', 'Rec Sports Facility', 'Convention Center',
                   'Campground', 'Natl Park', 'Place Of Worship',
                   'Other Entertainment']:
        return 'Recreation'
    elif value in ['Other', 'Public',
                   'Airport', 'Park', 'Library',
                   'Truck Stop', 'Rest Stop', 'Standalone Station', 'Rv Park',
                   'Parking Garage', 'Parking Lot', 'Pay Lot', 'Pay Garage', 'Street Parking',
                   'Gas Station', 'Fleet Garage']:
        return 'Public / Other'
    else:
        return 'Unknown'


def identify_start_hour(access_time):
    if pd.isna(access_time):
        return DEFAULT_HOURS_START

    access_time = access_time.lower()
    if '24 hours' in access_time or '24/7' in access_time:
        return '12:01am'

    time_match = re.findall(r'(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm))', access_time, re.IGNORECASE)
    if time_match:
        return time_match[0]

    if 'hours' in access_time:
        return '9am'
    if 'dawn' in access_time or 'sunrise' in access_time:
        return '6am'

    return DEFAULT_HOURS_START


def identify_end_hour(access_time):
    if pd.isna(access_time):
        return DEFAULT_HOURS_END

    access_time = access_time.lower()
    if '24 hours' in access_time or '24/7' in access_time:
        return '11:59pm'

    time_match = re.findall(r'(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm))', access_time, re.IGNORECASE)
    if time_match:
        return time_match[-1]

    if 'hours' in access_time:
        return '5pm'
    if 'dusk' in access_time or 'sunrise' in access_time:
        return '6pm'
    return DEFAULT_HOURS_END


def identify_access_hours(row):
    start = int(row['hours_start'])
    end = int(row['hours_end'])
    hours = np.zeros(24, dtype=int)

    if end > start:
        hours[start:end] = 1
    elif end < start:  # post-midnight
        hours[start:] = 1
        hours[:end] = 1

    return hours


######################
# IMPORT CHARGING STATION DATA

# download + format alternative fuel charging station data
data = requests.get(ALT_FUEL_URL + ALT_FUEL_PARAMETERS).json()
df = pd.DataFrame.from_records([feature['properties'] for feature in data['features']])
geometry_data = [feature['geometry']['coordinates'] for feature in data['features']]
df['geometry'] = pd.Series(geometry_data).apply(Point)
df = df[DF_COLS]

# check that 'id' is a unique column
assert df['id'].nunique() == len(df)
df['id'] = df['id'].astype(str)

# filter for only continental states
df = df[~df['state'].isin(DROP_STATES)].reset_index(drop=True)

# clean facility type
print(df['facility_type'].unique())
df['facility_type'] = df['facility_type'].str.replace('_', ' ')
df['facility_type'] = df['facility_type'].str.title()
df['facility_type'] = df['facility_type'].fillna('Unknown')
df['facility_type'] = df['facility_type'].apply(categorize_facilities)

######################
# ANALYZE HOURS OF ACCESS

# extract information on hours of access
df['hours_start'] = df['access_days_time'].apply(identify_start_hour).str.replace(' ', '')
df['hours_end'] = df['access_days_time'].apply(identify_end_hour).str.replace(' ', '')
# update format to hour of the day
df['hours_start'] = (pd.to_datetime(df['hours_start'], format='%I:%M%p', errors='coerce')
                     .fillna(pd.to_datetime(df['hours_start'], format='%I%p', errors='coerce')))
df['hours_end'] = (pd.to_datetime(df['hours_end'], format='%I:%M%p', errors='coerce')
                   .fillna(pd.to_datetime(df['hours_end'], format='%I%p', errors='coerce')))
df['hours_start'] = ((df['hours_start'].dt.hour + (df['hours_start'].dt.minute / 60))*2).round() / 2
df['hours_end'] = ((df['hours_end'].dt.hour + (df['hours_end'].dt.minute / 60))*2).round() / 2
# update edge case
df['hours_end'] = np.where(df['hours_end'] == 0, 24, df['hours_end'])
df['hours_end'] = np.where(df['hours_start'] == df['hours_end'], df['hours_start'] + 12, df['hours_end'])

# create dataframe with hours of access
hours_df = pd.DataFrame(df.apply(identify_access_hours, axis=1).tolist())
# merge charging stations + hours of access data
hours_df = pd.melt(pd.concat([df, hours_df], axis=1), id_vars=df.columns, var_name='hour', value_name='access')

######################
# VISUALIZE CHARGING STATIONS BY FACILITY TYPE

# create geodataframe from hours_df
gdf = gpd.GeoDataFrame(hours_df[['id', 'facility_type', 'geometry']].drop_duplicates(),
                       geometry='geometry', crs='EPSG:4326')
gdf = gdf.to_crs(epsg=3857)

# import + format map of the united states
us_map = gpd.read_file(US_SHAPEFILE).rename(columns=MAP_COLS)
us_map = us_map[MAP_COLS.values()]
us_map = us_map[~us_map['state'].isin(DROP_STATES)]
us_map = us_map.to_crs(epsg=3857)

# create figure for plots
f, ax = plt.subplots(figsize=(15, 6))

# plot us map + basemap
us_map.plot('state', ax=ax, alpha=0.3, cmap='Spectral')
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)

# plot  charging stations
gdf.plot(ax=ax, markersize=2, alpha=0.7,
         column='facility_type', cmap=plt.get_cmap('tab10'),
         legend=True, legend_kwds={'bbox_to_anchor': (1.05, 1), 'loc': 'upper left'})
ax.get_legend().set_title('Facility Type')
ax.set_title('Public EV Charging Stations in the U.S. (n=%s)' % f'{len(gdf):,}',
             fontsize=12, fontweight='bold')

# save figure
plt.savefig(OUTPUT_FOLDER + 'us_ev_charging_stations_facility.png')

######################
# VISUALIZE CHARGING STATIONS BY ACCESSIBLE HOURS

# format map data
hours_map = gpd.GeoDataFrame(hours_df, geometry='geometry', crs='EPSG:4326')
hours_map['longitude'] = hours_map['geometry'].x
hours_map['latitude'] = hours_map['geometry'].y
hours_map['access'] = hours_map['access'].replace({0: 'closed', 1: 'open'})

# only include 10,000 random stations to reduce html file size and keep under git limit
station_subset = hours_map[['id']].drop_duplicates().sample(6000)

hours_map = hours_map[hours_map['id'].isin(station_subset['id'].unique())]

# plot + format the map
fig = px.scatter_mapbox(hours_map, lat='latitude', lon='longitude', zoom=3,
                        title='<b>Public EV Charging Stations in the U.S.</b><br>Accessible Hours',
                        custom_data=['station_name', 'access_days_time', 'street_address', 'city', 'state', 'zip'],
                        animation_frame='hour', color='access', labels='station_name',
                        color_discrete_map={'open': '#64b57a', 'closed': '#d95252'},
                        opacity=0.7, width=800, height=600)
fig.update_layout(mapbox={'style': 'open-street-map', 'zoom': 3},
                  margin={'l': 0, 'r': 0, 't': 80, 'b': 0},
                  autosize=False,
                  legend_title=None)
# add key information on hover
fig.update_traces(hovertemplate='<b>%{customdata[0]}</b><br>' +
                                '<i>%{customdata[1]}</i><br><br>' +
                                '%{customdata[2]}<br>%{customdata[3]}, %{customdata[4]} %{customdata[5]}')
fig.show()

# save smaller version of file

fig.write_html(OUTPUT_FOLDER + 'us_ev_charging_stations_hours.html')

