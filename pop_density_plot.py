#!/usr/bin/env python

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
custom_params = {"axes.spines.right": False, "axes.spines.top": False,
                 "axes.spines.left": False, "axes.spines.bottom": False,
                 "xtick.labelbottom":False, "ytick.labelleft": False,
                 "xtick.bottom": False, "ytick.left": False,}
sns.set_theme(style="white", rc=custom_params)
#  data from https://ec.europa.eu/eurostat/web/gisco/geodata/reference-data/population-distribution-demography/geostat
population_1k_data = Path("./GEOSTAT/GEOSTAT_grid_POP_1K_2011_V2_0_1.csv")
df = pd.read_csv(population_1k_data)

# column contains different datatypes
# we don't use it so drop it
df = df.drop(columns='TOT_P_CON_DT') 

# Get island of Ireland 
df = df.loc[(df['CNTR_CODE'] == 'IE') | (df['CNTR_CODE'] == 'UK')]
grid_north = df['GRD_ID'].str[4:8].astype(float)
grid_east = df['GRD_ID'].str[9:].astype(float)
df['GRID_NORTH'] = grid_north
df['GRID_EAST'] = grid_east
df = df.loc[(df['GRID_EAST'] < 3333.0)]
df = df.drop(df[(df['CNTR_CODE'] == 'UK') & (df['GRID_NORTH'] > 3707.0)].index)
df = df.drop(df[(df['CNTR_CODE'] == 'UK') & (df['GRID_NORTH'] < 3517.0)].index)

# prepare for plot
# only take every 10 longitudes because I'm too lazy to average
norths = np.sort(pd.unique(df['GRID_NORTH']))[::10]
df['PLOT_POP'] = df['GRID_NORTH'] + 100*(df['TOT_P']/df['TOT_P'].max())

plt.figure(figsize=(9,9))
# plt.figure()
for north in norths:
    sns.lineplot(df[df['GRID_NORTH'] == north],
                 x = 'GRID_EAST', y='PLOT_POP',
                 color='forestgreen',
                 drawstyle='steps',
                 linewidth=2.5)

plt.savefig("./Ireland_1k_poulation.png")
plt.show()


"""
Conversion to/from Lambert Azimuthal Equal Area (LAEA) grid coordinate
and latitude longitude
TODO: add units
"""
R = 6378137.0 #m
#"Central_Meridian",10.0],["Latitude_Of_Origin",52.0
lat_0 = 52.0*(np.pi/180)
lon_0 = 10.0*(np.pi/180)
false_easting = 4321000 #m
false_northing = 3210000

def rho(x, y):
    return np.sqrt(x**2+y**2)
def c(x, y):
    return 2*np.arcsin(rho(x,y)/(2*R))
def laea_to_latlon(x, y):

    x = (x*1000) - false_easting
    y = (y*1000) - false_northing
    lon = lon_0 \
        + np.arctan( 
                (x*np.sin(c(x,y))) \
                / ((rho(x,y)*np.cos(lat_0)*np.cos(c(x,y))) \
                   -(y*np.sin(lat_0)*np.sin(c(x,y)))) )
    
    lat = np.arcsin(
        (np.cos(c(x,y))*np.sin(lat_0)) \
        + (y*np.sin(c(x,y))*np.cos(lat_0))/(rho(x,y))
        
    )
    
    return lat*(180/np.pi), lon*(180/np.pi)

def kprime(lat, lon):
    return np.sqrt(2/(1 + 
                      np.sin(lat_0)*np.sin(lat) +
                      np.cos(lat_0)*np.cos(lat)*np.cos(lon-lon_0)))
def latlon_to_laea(lat, lon):
    lat = lat*(np.pi/180)
    lon = lon*(np.pi/180)
    x = R*kprime(lat, lon)*np.cos(lat)*np.sin(lon-lon_0)
    y = R*kprime(lat, lon)*(np.cos(lat_0)*np.sin(lat)-np.sin(lat_0)*np.cos(lat)*np.cos(lon-lon_0))
    x += false_easting
    y += false_northing
    return x, y