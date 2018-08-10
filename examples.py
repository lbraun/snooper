# Examples

#============================
# snooper.py
#============================

import snooper

path_to_file = "Location History.json"
snooper.process_file(path_to_file)

snooper.json_to_csv(path_to_file)
snooper.json_to_shapefile(path_to_file)

files = [
    "Location History 1.json",
    "Location History 2.json",
    "Location History 3.json",
    "Location History 4.json",
    "Location History 5.json",
    "Location History 6.json",
]

snooper.process_file(files)
