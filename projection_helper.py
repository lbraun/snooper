# -*- coding: utf-8 -*-
"""
Created on Tue Aug  7 11:13:11 2018

@author: willi
"""

import numpy as np
from osgeo import ogr, osr
import os

# filedir = r'D:\MASTER_GEOTECH_2S\LastCourse\FinalProject\Data'

# #path to the shapefile
# shp_filename = os.path.join(filedir,'shp','participant_6.shp')

# # Path to output shapefile
# output_filename = os.path.join(filedir, 'shp','participant_6_pr.shp')


def generate_segments(shp_filename, target_projection_id, output_filename):
    # Load the shapefile and extract the layer
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shapefile = driver.Open(shp_filename, 0)

    if shapefile == None:
        print(f"Shapefile '{shp_filename}' contains no data. Skipping...")
        return

    layer = shapefile.GetLayer()

    #=============================
    # ## Projection of the points
    #=============================

    # Define output projection
    target_projection = osr.SpatialReference()
    target_projection.ImportFromEPSG(target_projection_id)

    # Define input projection
    # Assume data comes in the WGS 84 projection
    source_projection = osr.SpatialReference()
    source_projection.ImportFromEPSG(4326)
    transformation = osr.CoordinateTransformation(source_projection, target_projection)

    # If the output file already exists, delete it
    if os.path.exists(output_filename):
        print(f"A file with the name '{output_filename}' already exists. Deleting...")
        driver.DeleteDataSource(output_filename)

    # Create the output shapefile
    print("Creating output shapefile...")
    output_shapefile = driver.CreateDataSource(output_filename)

    # Create a layer on the output shapefile with target_projection
    output_layer = output_shapefile.CreateLayer('locations', target_projection, ogr.wkbPoint)

    # Create output layer with the same schema as the original layer
    output_layer.CreateFields(layer.schema)
    output_layer_defn = output_layer.GetLayerDefn()
    output_feature = ogr.Feature(output_layer_defn)

    # Loop over all the features and change their spatial reference
    for feature in layer:
        point = feature.geometry()
        point.Transform(transformation)
        output_feature.SetGeometry(point)

        # Set the feature's fields with the attributes from the original feature
        for i in range(feature.GetFieldCount()):
            value = feature.GetField(i)
            output_feature.SetField(i, value)

        output_layer.CreateFeature(output_feature)

    print('Done!')
    return output_filename
