# -*- coding: utf-8 -*-
"""
Created on Mon Aug  6 16:21:21 2018

@author: willi
"""


import os
from osgeo import gdal, ogr
import numpy as np
import datetime

data_directory = "/Users/lucasbraun/Google Drive/Grad School/Semester 2/Data into Knowledge/TDTK Final Project/Data/netCDF/"

def add_climate_data(shp_filename, data_directory=data_directory):
    year = 2018
    variables = ["tmin", "tmax", "percip"]

    for variable in variables:
        netcdf_filename = f"{data_directory}{variable}.{year}.nc"
        masknetcdf(netcdf_filename, shp_filename, variable)

def masknetcdf(netcdf_filename, shp_filename, cl_field=None):
    if cl_field == None:
        # If no field is provided, assume first part of file name is the field to use
        head, tail = os.path.split(netcdf_filename)
        cl_field = tail.split(".")[0]

    #Open dataset
    data_source = gdal.Open(netcdf_filename)
    #Number of columns of each layer
    cols =data_source.RasterXSize
    #Number of rows of each layer
    rows = data_source.RasterYSize
    #Number of bands of each layer
    nbands = data_source.RasterCount
    #Year of the netcdf file
    year = int(netcdf_filename.split('.')[-2])
    #========================================
    #Importing data by bands as a dictionary
    #========================================
    datach = {}
    #First day of the year as reference
    yearc =  str(year) + "-01-01"
    #Converting year in a datatime object
    fi_date = datetime.datetime.strptime(yearc,"%Y-%m-%d").date()
    #for loop of the layers that contains the netcdf file
    for i in range(1,nbands+1):
        index_date = fi_date + datetime.timedelta(days=i-1)
        in_band = data_source.GetRasterBand(i)
        #Converting default nan in np.na
        in_band_wnan = in_band.ReadAsArray()
        in_band_wnan[in_band_wnan==-9.9692100e+36] = np.nan
        datach[index_date.strftime("%Y-%m-%d")] =  in_band_wnan

    #====================================
    #parameters of transformation
    #====================================
    x = 0.5*cols-rows
    delta_Lon = 360/cols
    delta_Lat = 180/(rows+x)
    if x==0:
        LonUpper_Left = 0
        LatUpper_Left = 90
    else:
        LonUpper_Left = -delta_Lon/2
        LatUpper_Left = delta_Lat*(rows/2)
    gt = [LonUpper_Left,delta_Lon, 0,LatUpper_Left,0,-delta_Lat ]
    #Inverse affine transformation
    inv_gt = gdal.InvGeoTransform(gt)
    inv_gt
    #=====================================================================
    #Importing shapefile and transforming coordinates to rows and columns
    #=====================================================================
    #Calling driver
    driver = ogr.GetDriverByName('ESRI Shapefile')
    #Open dataset
    datasource1 = driver.Open(shp_filename,1)
    #get layer
    layer = datasource1.GetLayer()
    #get number of features
    fc = layer.GetFeatureCount()
    #creating lists for rows, columns and time index
    xt_p = []
    yt_p = []
    dayc = []
    for fea in layer:
        #time
        a = fea.GetField("timestamp")[0:10]
        dayc.append(a)
        #coord
        pt = fea.geometry()
        #Transforming coord
        xt, yt = gdal.ApplyGeoTransform(inv_gt,pt.GetX(),pt.GetY())
        xt_p.append(xt)
        yt_p.append(yt)
    #=================================
    #Extracting values by time
    #=================================
    #converting list of days to array
    array_indexday = np.array(dayc)
    #Creating a vector of nan values
    value = np.zeros(fc)
    value[value==0] = np.nan
    #for loop to extract values by time
    for j in np.unique(dayc):
        #Condition about the year of interest
        year_d = datetime.datetime.strptime(j,"%Y-%m-%d").year
        if year_d == year:
            #Match day of the features with the day of the band array
            index = np.where(array_indexday == j)[0].tolist()
            in_band = datach[j]
            #Extracting values of the layer that correspond to certain time
            for k in range(0,len(index)):
                data = in_band[int(yt_p[index[k]]),int(xt_p[index[k]])]
                value[index[k]] = data
        else:
            continue
    #============================
    #Loading values to shapefile
    #============================
    #Calling the shapefile again but in edition version (1)
    driver = ogr.GetDriverByName('ESRI Shapefile')
    datasource2 = driver.Open(shp_filename,1)
    layer2 = datasource2.GetLayer()
    #reset index
    datasource2.SyncToDisk()
    #List of the fields of the shapefile
    schema = []
    ldefn = layer2.GetLayerDefn()
    for n in range(ldefn.GetFieldCount()):
        fdefn = ldefn.GetFieldDefn(n)
        schema.append(fdefn.name)
    #so, if the field exists this fucntion update the field, otherwise, it will create
    #a new field with the specified name
    if np.any(np.array(schema) == cl_field):
        i=0
        #for loop quering the existency of the value for certain period
        for fe in layer2:
            year_2 = datetime.datetime.strptime(dayc[i],"%Y-%m-%d").year
            if year_2 == year:
                fe.SetField(cl_field,value[i])
                layer2.SetFeature(fe)
            i = i + 1
    else:
        #Creating the the new field
        new_field = ogr.FieldDefn(cl_field,ogr.OFTReal)
        layer2.CreateField(new_field)
        i=0
        for fe in layer2:
            fe.SetField(cl_field,value[i])
            layer2.SetFeature(fe)
            i = i + 1
    #destroy data source shapefile
    datasource1.Destroy()
    datasource2.Destroy()
    #Clos source netcdf
    data_source= None
    del value
    print(f"Done! Year: {year}; Field {cl_field}")
