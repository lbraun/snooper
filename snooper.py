import csv
import location_history_parser
import shapefile_helper
import climate_data_helper
import projection_helper
import segments_helper


#============================
# Complete processing
#============================

def process_files(filenames, filters = {}):
    for filename in filenames:
        process_file(filename, filters)

def process_file(filename, filters = {}):
    print(f"\n### Processing {filename}...")
    json_to_csv(filename, filters)
    shp_filename = json_to_shapefile(filename, filters)

    climate_data_helper.add_climate_data(shapefile)

    projected_shapefile = shapefile.replace("Point Shapefiles", "Projected Point Shapefiles")
    projected_shapefile = projected_shapefile.replace(".shp", "_projected.shp")
    projection_helper.project(shapefile, 32632, projected_shapefile)

    segments_shapefile = shapefile.replace("Point Shapefiles", "Segment Shapefiles")
    segments_shapefile = segments_shapefile.replace(".shp", "_segments.shp")
    segments_helper.generate_segments(projected_shapefile, segments_shapefile)


#============================
# CSV creation
#============================

def json_to_csv(filename, filters = {}):
    print(f"Parsing file '{filename}'...")
    data = location_history_parser.parse_json_file_as_rows(filename)

    output_filename = filename.replace(".json", ".csv")
    print(f"Writing {len(data)} row(s) to '{output_filename}'...")
    write_csv_file(output_filename, data)
    print("Done!")

def write_csv_file(filename, rows):
    with open(filename, 'w') as output:
        csv_writer = csv.writer(output, lineterminator='\n')
        csv_writer.writerows(rows)


#============================
# Shapefile creation
#============================

def json_to_shapefile(filename, filters = {}):
    print(f"Parsing file '{filename}'...")
    data_points = location_history_parser.parse_json_file(filename)["locations"]

    output_filename = filename.replace(".json", ".shp")

    print(f"Writing {len(data_points)} row(s) to '{output_filename}'...")
    shapefile_helper.json_to_shapefile(data_points, output_filename)

    print("Done!")
    return(output_filename)

def filters_example():
    filters = {
        "start": datetime(2018, 4, 1),
        "end": datetime(2018, 8, 1),
        "bbox": {
            "min_lat": -90.0,
            "min_lon": 6.0,
            "max_lat": 90.0,
            "max_lon": 12.0,
        }
    }
    return filters
