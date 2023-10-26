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
