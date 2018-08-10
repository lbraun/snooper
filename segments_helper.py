# -*- coding: utf-8 -*-
"""
Created on Tue Aug  7 12:53:12 2018

@author: willi
"""

from math import sqrt
from datetime import datetime
import numpy as np
from osgeo import ogr, osr
import os

# filedir = r'D:\MASTER_GEOTECH_2S\LastCourse\FinalProject\Data'

# #path to the shapefile
# points_shp_filename = os.path.join(filedir, 'shp','participant_6_pr.shp')

# # Path to output shapefile
# segments_shp_filename = os.path.join(filedir, 'shp','segments_participant_6.shp')


def generate_segments(points_shp_filename, segments_shp_filename):
    # Load the shapefile and extract the layer
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shapefile = driver.Open(points_shp_filename, 0)

    if shapefile == None:
        print(f"Shapefile '{points_shp_filename}' contains no data. Skipping...")
        return

    layer = shapefile.GetLayer()

    # If the output file already exists, delete it
    if os.path.exists(segments_shp_filename):
        print(f"A file with the name '{segments_shp_filename}' already exists. Deleting...")
        driver.DeleteDataSource(segments_shp_filename)

    # Create the output shapefile
    lines_ds = driver.CreateDataSource(segments_shp_filename)
    # Set the spatial reference, WGS84
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(32632)
    #=================
    # Lines
    #=================

    # Create a new layer within the output shapefile
    lines = lines_ds.CreateLayer('lines', srs, ogr.wkbLineString)

    fields = [
        {'name': 'id_person',  'type': ogr.OFTString},
        {'name': 'start_time', 'type': ogr.OFTString},
        {'name': 'end_time',   'type': ogr.OFTString},
        {'name': 'distance',   'type': ogr.OFTReal},
        {'name': 'duration',   'type': ogr.OFTReal},
        {'name': 'speed',      'type': ogr.OFTReal},
        {'name': 'accuracy',   'type': ogr.OFTReal},
        {'name': 'activity',   'type': ogr.OFTString},
        {'name': 'confidence', 'type': ogr.OFTReal},
        {'name': 'tmax',       'type': ogr.OFTReal},
        {'name': 'tmin',       'type': ogr.OFTReal},
        {'name': 'precip',     'type': ogr.OFTReal},
    ]

    for field in fields:
        field_definition = ogr.FieldDefn(field['name'], ogr.OFTReal['type'])
        lines.CreateField(field_definition)

    #===========================================
    # Function to calculate distance
    #===========================================

    def euclideandist(x1,y1,x2,y2):
        deltax = x1 - x2
        deltay = y1 - y2
        d = sqrt(deltax**2 + deltay**2)
        return(d)

    # Secondly, we wrote a function that calculates the duration of each segment. This is simply the difference between the timestamp of the startpoint of the segment and the timestamp of the endpoint of the segment. In our data, the timestamp of each point is stored as a string. The module datetime was used to transform these strings into datetime objects, such that substractions of timestamps coudl be done correctly. The returned value will be duration in seconds.

    # Define the duration function
    def timedif(time1, time2):
        # Convert to datetime objects
        time1 = datetime.strptime(time1, '%Y-%m-%d %H:%M:%S')
        time2 = datetime.strptime(time2, '%Y-%m-%d %H:%M:%S')
        # Convert to numeric (seconds from 01-01-1970 UTC)
        time1 = time1.timestamp()
        time2 = time2.timestamp()
        # Calculate time difference
        dT = time2 - time1
        return dT

    #======================
    # Get id of participants
    #======================
    idn_list = []
    for feat in layer:
        idn = feat.GetField("id_person")
        idn_list.append(idn)

    layer.ResetReading()
    idents = np.unique(idn_list)

    #======================
    # For loop segments
    #======================

    # Select an individual goose base on its unique ID and create the corresponding segments, including attributes
    for i in idents:
        # Create empty lists to store the geometry and attribute values of each point in
        x_list = [] # X coordinates
        y_list = [] # Y coordinates
        time_list = [] # Timestamps
        accur_list = [] # Accuracy
        activ_list = [] # Activity
        confi_list = [] # Confidence
        Tmax_list = [] # Tmeperature max
        Tmin_list = [] # Temperature min
        prec_list = [] # Precipitation
        # Store the geometry and attribute values of each point in lists
        for ft in layer:
            idn = ft.GetField('id_person')
            if idn == i:
                pt = ft.geometry()
                x = pt.GetX()
                y = pt.GetY()
                time= ft.GetField('timestamp')
                accur = ft.GetField('accuracy')
                activ = ft.GetField('activity')
                confi = ft.GetField('confidence')
                Tmax = ft.GetField('tmax')
                Tmin = ft.GetField('tmin')
                prec = ft.GetField('precip')
                x_list.append(x)
                y_list.append(y)
                time_list.append(time)
                accur_list.append(accur)
                activ_list.append(activ)
                confi_list.append(confi)
                Tmax_list.append(Tmax)
                Tmin_list.append(Tmin)
                prec_list.append(prec)
        layer.ResetReading()

        # Create each segment one by one
        for j in range(0, len(x_list)-1):
            # Get geometry and attribute values of startpoint and endpoint of the segment
            stx = x_list[j]
            enx = x_list[j+1]
            sty = y_list[j]
            eny = y_list[j+1]
            start_time = time_list[j]
            end_time = time_list[j+1]
            stTmax = Tmax_list[j]
            enTmax = Tmax_list[j+1]
            stTmin = Tmin_list[j]
            enTmin = Tmin_list[j+1]
            stprec = prec_list[j]
            enprec = prec_list[j+1]
            # Create a segment between the start and end point
            seg = ogr.Geometry(ogr.wkbLineString)
            seg.AddPoint(stx, sty)
            seg.AddPoint(enx, eny)
            # Create a new feature
            feat = ogr.Feature(lines.GetLayerDefn())
            # Add the linestring geometry to the feature
            feat.SetGeometry(seg)
            # Add the corresponding goose ID to the 'idn_ident' field of the feature
            feat.SetField('id_person', i)
            # Add start and end time by segment
            feat.SetField('start_time', start_time)
            feat.SetField('end_time', end_time)
            # Calculate distance and add this value to the corresponding field
            distance = euclideandist(stx, sty, enx, eny)
            feat.SetField('distance', distance)
            # Calculate duration and add this value to the corresponding field
            sttime1 = start_time.split('.')[0]
            entime1 = end_time.split('.')[0]
            duration = timedif(sttime1, entime1)
            feat.SetField('duration', duration)
            # Activity, I will select the start point
            accurl = accur_list[j]
            feat.SetField('accuracy', accurl)
            # Activity, I will select the start point
            act = activ_list[j]
            feat.SetField('activity', act)
            # Confidence, I will select the start point
            conf = confi_list[j]
            feat.SetField('confidence', conf)
            # Calculate speed  and add this value to the corresponding field
            if duration == 0:
                speed = 0
            else:
                speed = distance/duration
            feat.SetField('speed', speed)

            # Calculate average weather values and add these values to the corresponding fields
            Tmaxi = (stTmax + enTmax)/2
            feat.SetField('tmax', Tmaxi)
            Tmini = (stTmin + enTmin)/2
            feat.SetField('tmin', Tmini)
            prec = (stprec + enprec)/2
            feat.SetField('precip', prec)
            # Create the feature with its field
            lines.CreateFeature(feat)
            # Dereference the feature
            feat = None

    # Close the data source
    lines_ds = None
    print('Done!')










