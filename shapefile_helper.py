# -*- coding: utf-8 -*-
"""
Created on Mon Aug  6 16:21:21 2018

@author: willi
"""

import os
from osgeo import ogr ,osr
import csv

filedir = r'D:\MASTER_GEOTECH_2S\LastCourse\FinalProject\Data'

#Output shapefile
filename_out_shp = os.path.join(filedir,'shp','Lucas_points.shp')

#Loading csv
filename_csv = os.path.join(filedir,'csv','Lucas Location History.csv')

def json_to_shapefile(data_points, output_filename, identifier=None):
    if identifier == None:
        head, tail = os.path.split(output_filename)
        identifier = tail.replace(".shp", "")

    # Initialize OGR driver
    driver = ogr.GetDriverByName('Esri Shapefile')

    # If the output file already exists, delete it
    if os.path.exists(output_filename):
        print(f"A file with the name '{output_filename}' already exists. Deleting...")
        driver.DeleteDataSource(output_filename)

    # Create the shapefile
    print("Creating shapefile...")
    shapefile = driver.CreateDataSource(output_filename)

    # Create main layer with WGS 84 reference system
    spatial_reference_system = osr.SpatialReference()
    spatial_reference_system.ImportFromEPSG(4326)
    layer = shapefile.CreateLayer('locations', spatial_reference_system, ogr.wkbPoint)

    # Add fields to the layer
    field_definitions = [
        ogr.FieldDefn('id', ogr.OFTString),
        ogr.FieldDefn('id_person', ogr.OFTString),
        ogr.FieldDefn('timestamp', ogr.OFTString),
        ogr.FieldDefn('latitude', ogr.OFTReal),
        ogr.FieldDefn('longitude', ogr.OFTReal),
        ogr.FieldDefn('accuracy', ogr.OFTReal),
        # ogr.FieldDefn('velocity', ogr.OFTReal),
        # ogr.FieldDefn('heading', ogr.OFTReal),
        # ogr.FieldDefn('altitude', ogr.OFTReal),
        # ogr.FieldDefn('v_accuracy', ogr.OFTReal),
        ogr.FieldDefn('activity', ogr.OFTString),
        ogr.FieldDefn('confidence', ogr.OFTReal),
    ]
    for field_definition in field_definitions:
        layer.CreateField(field_definition)

    # Add a feature to the layer for each data_point
    print("Adding features...")
    for index, data_point in enumerate(data_points):
        # Initialize a new feature (geometry)
        feature = ogr.Feature(layer.GetLayerDefn())

        # Set the geometry of the new feature
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(float(data_point["lon"]), float(data_point["lat"]))
        feature.SetGeometry(point)

        # Set the attributes of the new feature
        # TODO: Handle "" values for OFTReal fields (should not become zeros)
        feature.SetField('id', index)
        feature.SetField('id_person', identifier)
        feature.SetField('timestamp', str(data_point["timestamp"]))
        feature.SetField('latitude', data_point["lat"])
        feature.SetField('longitude', data_point["lon"])
        feature.SetField('accuracy', data_point["accuracy"])
        # feature.SetField('velocity', data_point["velocity"])
        # feature.SetField('heading', data_point["heading"])
        # feature.SetField('altitude', data_point["altitude"])
        # feature.SetField('v_accuracy', data_point["vertical_accuracy"])
        feature.SetField('activity', data_point["activity"])
        feature.SetField('confidence', data_point["activity_confidence"])

        # Add the feature to the layer
        layer.CreateFeature(feature)


def csv_to_shp(filename_csv, name_person):

    #============================
    #Importing shapefile
    #============================
    infile = open(filename_csv, 'r')  # CSV file
    table = []
    csv_reader = csv.reader(infile)
    for row in csv_reader:
        table.append(row)
    infile.close()

    #table = table[0:1000]

    #len(table)
    #============================
    #Creating shapefile
    #============================
    # Now convert it to a shapefile with OGR
    driver = ogr.GetDriverByName('Esri Shapefile')
    #if the output shapefile that we create already exists, delete it
    if os.path.exists(filename_out_shp):
        print('deleting')
        driver.DeleteDataSource(filename_out_shp)

    ds = driver.CreateDataSource(filename_out_shp)
    #reference system
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    layer = ds.CreateLayer('pt', srs , ogr.wkbPoint)
    # Add new fields
    id_def = ogr.FieldDefn('id', ogr.OFTString) #ID
    layer.CreateField(id_def)
    idp_def = ogr.FieldDefn('id_person', ogr.OFTString) #ID
    layer.CreateField(idp_def)
    tim_def = ogr.FieldDefn('timestamp', ogr.OFTString) #timestamp
    layer.CreateField(tim_def)
    lat_def = ogr.FieldDefn('latitud', ogr.OFTReal) #latitud
    layer.CreateField(lat_def)
    lon_def = ogr.FieldDefn('longitud', ogr.OFTReal) #latitud
    layer.CreateField(lon_def)
    act_def = ogr.FieldDefn('activity', ogr.OFTString) #latitud
    layer.CreateField(act_def)

    #for loop geometries
    j=0
    for rowa in table:
        if j==0:
            j = j+1
            continue
        else:
            # Create a new feature (attribute and geometry)
            point = ogr.Geometry(ogr.wkbPoint)
            point.AddPoint(float(rowa[2]), float(rowa[1]))
            feat = ogr.Feature(layer.GetLayerDefn())
            feat.SetGeometry(point)
            # add ID
            feat.SetField('id', j)
            # add ID
            feat.SetField('id_person', name_person)
            # add timestamp
            feat.SetField('timestamp', rowa[0])
            # add latitud
            feat.SetField('latitud', float(rowa[1]))
            # add longitud
            feat.SetField('longitud', float(rowa[2]))
           # add longitud
            feat.SetField('activity', rowa[-2])
            # Make a geometry, from Shapely object
            layer.CreateFeature(feat)
            feat = point = None  # destroy these
            j = j+1
