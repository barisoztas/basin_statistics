'''THIS CODE PROVIDES STATISTICS AS .CSV FILES FOR ANY GIVEN NETCDF FILE IF SHAPEFILE IS PROVIDED'''

'''This is specifically writen for Burdur basin & its' temperature and precipitation statistics from ERA5 reanalysis datasets'''
import pandas as pd
import datetime
from datetime import timedelta
import xarray as xr
import rasterio as rio
import geopandas as gpd
import rasterstats as rstats

start = datetime.datetime.strptime("19790101", "%Y%m%d")
end = datetime.datetime.strptime("20201231", "%Y%m%d")
date_list2 = [start + timedelta(n) for n in range(int((end - start).days) + 1)]

df3 = pd.DataFrame({'date':date_list2})


df3['month_year'] = df3['date'].dt.to_period('M')
df3['year']= df3['date'].dt.year
df3['months']= df3['date'].dt.month

dateList3 = df3['month_year'].astype(str).values.tolist()
dateList3 = sorted(list(set(dateList3)))
yearList = df3['year'].astype(str).values.tolist()
monthList1 = df3['months'].astype(str).values.tolist()
uniquemonthList=sorted(map(int,(list(set(monthList1)))))
uniqueyearList= sorted(list(set(yearList)))

yearList = [ele for ele in uniqueyearList for i in range(12)]

monthList = sorted(list(map(int,uniquemonthList)))*42

shp_fo = "D:/Drivers/Hidrosaf_notes/havza/burdur_wgs.shp"
nc_fo = "D:/Drivers/Hidrosaf_notes/havza/temperature.nc"
nc_fo2 = "D:/Drivers/Hidrosaf_notes/havza/total_precipitation.nc"
# import packages


# load and read shp-file with geopandas

shp_df = gpd.read_file(shp_fo)

# load and read netCDF-file to dataset and get datarray for variable


#total precipitation
nc_ds = xr.open_dataset(nc_fo)
nc_var = nc_ds['tp']
nc_var = nc_var[:,0,:,:]

#2m temperature
nc_ds2 = xr.open_dataset(nc_fo2)
nc_var2 = nc_ds2['t2m']
nc_var2 = nc_var2[:,0,:,:]
# get all years for which we have data in nc-file
years_ = nc_ds['time'] #precipitation
years_2 = nc_ds2['time'] #temperature
# get affine of nc-file with rasterio
affine = rio.open(nc_fo).transform
affine2 = rio.open(nc_fo2).transform
#
# # go through all years for precipitation (sum)
pd = pd.DataFrame(columns=['sum'])
for year in years_:
    # get values of variable pear year
    nc_arr = nc_var.sel(time=year)
    nc_arr_vals = nc_arr.values
    # go through all geometries and compute zonal statistics
    for i in range(len(shp_df)):
        stat = rstats.zonal_stats(shp_df.geometry, nc_arr_vals, affine=affine, stats="sum")
        stats = stat[0]

        pd = pd.append(
        {'sum':stats['sum']}, ignore_index = True)

pd_ = pd.assign(years=yearList)
pd_['months'] = monthList
pd_.to_csv('prec_son.csv', index=False)



## # go through all years for temperature (avg)

pd2 = pd.DataFrame(columns=['mean'])
for year in years_:
    # get values of variable pear year
    nc_arr2 = nc_var2.sel(time=year)
    nc_arr_vals2 = nc_arr2.values
    # go through all geometries and compute zonal statistics
    for i in range(len(shp_df)):
        stat = rstats.zonal_stats(shp_df.geometry, nc_arr_vals2, affine=affine2, stats="mean")
        stats = stat[0]

        pd = pd.append(
        {'sum':stats['sum']}, ignore_index = True)

pd_2 = pd2.assign(years=yearList)
pd_2['months'] = monthList
pd_2.to_csv('temp_son.csv', index=False)

