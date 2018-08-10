import json
from datetime import datetime

def load_json_file(filename):
    with open(filename) as json_file:
        return json.load(json_file)

def parse_json_file(filename):
    print("Loading JSON file...")
    raw_json_data = load_json_file(filename)
    print("Parsing JSON data...")
    parsed_json_data = parse_json_data(raw_json_data)

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

    print("Filtering JSON data...")
    filtered_json_data = filter_json_data(parsed_json_data, filters=filters)
    print("Sorting JSON data...")
    sorted_json_data = sort_json_data(filtered_json_data, 'timestamp')
    return sorted_json_data

def parse_json_file_as_rows(filename):
    sorted_json_data = parse_json_file(filename)
    rows = rowify_json_data(sorted_json_data)
    return rows

def parse_json_data(raw_json_data):
    parsed_data_points = []
    for data_point in raw_json_data["locations"]:
        parsed_data_points.append(parse_data_point(data_point))
    return {"locations": parsed_data_points}

def filter_json_data(parsed_json_data, filters={}):
    filtered_data_points = []
    for data_point in parsed_json_data["locations"]:
        if check_against_filters(data_point, filters):
            filtered_data_points.append(data_point)
    return {"locations": filtered_data_points}

def sort_json_data(filtered_json_data, sort_key="timestamp"):
    filtered_json_data["locations"].sort(key=lambda data_point: data_point[sort_key])
    return filtered_json_data

def rowify_json_data(sorted_json_data):
    headers = [
        "timestamp",
        "latitude",
        "longitude",
        "accuracy",
        "velocity",
        "heading",
        "altitude",
        "vertical_accuracy",
        "activity",
        "activity_confidence",
    ]
    rows = [headers]
    for data_point in sorted_json_data["locations"]:
        row = [
            str(data_point.get("timestamp")),
            data_point["lat"],
            data_point["lon"],
            data_point["accuracy"],
            data_point["velocity"],
            data_point["heading"],
            data_point["altitude"],
            data_point["vertical_accuracy"],
            data_point["activity"],
            data_point["activity_confidence"],
        ]
        rows.append(row)
    return rows


#============================
# Parsing helper methods
#============================

def parse_activity(activity):
    if activity == "":
        return ["", ""]
    first_activity = activity[0]
    classifications = first_activity["activity"]
    best_classification = classifications[0]
    return [best_classification["type"], best_classification["confidence"]]

def parse_timestamp(t):
    return datetime.utcfromtimestamp(int(t) / 1000)

def parse_data_point(data_point):
    data_point["timestamp"] = parse_timestamp(data_point.get("timestampMs"))
    data_point["lat"] = data_point.get("latitudeE7") / 1e7
    data_point["lon"] = data_point.get("longitudeE7") / 1e7
    data_point["accuracy"] = data_point.get("accuracy", "")
    data_point["velocity"] = data_point.get("velocity", "")
    data_point["heading"] = data_point.get("heading", "")
    data_point["altitude"] = data_point.get("altitude", "")
    data_point["vertical_accuracy"] = data_point.get("verticalAccuracy", "")
    data_point["activity"], data_point["activity_confidence"] = parse_activity(data_point.get("activity", ""))
    return data_point


#============================
# Filtering helper methods
#============================

def check_against_filters(data_point, filters):
    start = filters.get("start", False)
    end = filters.get("end", False)
    bbox = filters.get("bbox", False)

    # Skip data from before the provided start datetime
    if start and (data_point["timestamp"] <= start):
        return False

    # Skip data from after the provided end datetime
    if end and (end < data_point["timestamp"]):
        return False

    # Skip data_points outside of bounding box
    if (bbox
        and ((data_point["lat"] < bbox["min_lat"])
            or (data_point["lat"] > bbox["max_lat"])
            or (data_point["lon"] < bbox["min_lon"])
            or (data_point["lon"] > bbox["max_lon"]))):
        return False

    # Skip data that hasn't been assigned an activity category
    if len(data_point["activity"]) == 0:
        return False

    # If data_point passes all filters, return True
    return True


#============================
# Datetime helper methods
#============================

def d(timestamp):
    return str(parse_timestamp(timestamp))

def create_timestamp(datetime):
    return datetime.strftime("%s%f")

def t(datetime):
    return create_timestamp(datetime)
