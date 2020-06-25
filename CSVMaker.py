import os
import datetime
import json
import pandas as pd

day_span = 2
num_stations = 5
measurements_dir = os.path.join(os.path.dirname(__file__), 'Measurements')

def get_neighbour(file_name, shift):
    fileList = os.listdir(measurements_dir)
    try:
        index = fileList.index(file_name)
        if index + shift < 0 or index + shift >= len(fileList):
            return None
        return os.path.join(measurements_dir, fileList[index + shift])
    except ValueError:
        return None


def fits_with_span(file_name):
    return get_neighbour(file_name, -day_span) != None and get_neighbour(file_name, day_span) != None

def get_closest_stations():
    stations = {}
    with open('StationsForMeasurement.json') as f:
        stations = {station['id']: {'latitude': station['latitude'], 'longitude': station['longitude'], 'elevation': station['elevation']} for station in json.load(f)}
    sorted_stations = {id: None for id in stations.keys()}
    for id in sorted_stations:
        sorted_stations[id]  = sorted(stations.keys(), key=lambda station: (stations[station]['longitude'] - stations[id]['longitude']) ** 2
         + (stations[station]['latitude'] - stations[id]['latitude']) ** 2)
    return sorted_stations

closest_stations = get_closest_stations()

def get_best_available_stations(sorted_row, all_available_stations):
    best_available_stations = []
    i = 1
    while i < len(sorted_row) and len(best_available_stations) < num_stations:
        if sorted_row[i] in all_available_stations.keys():
            best_available_stations.append(all_available_stations[sorted_row[i]])
        i += 1
    return best_available_stations

def get_features_for_file(file_name):
    station_values = {}
    with open(os.path.join(measurements_dir, file_name)) as f:
        station_values = json.load(f)
    features = {value: [station_values[station].get(value) for station in station_values] for value in ['latitude', 'longitude', 'elevation', 'TMAX', 'TMIN', 'PRCP']}
    for i in range(1, num_stations + 1):
        for value in ['latitude_', 'longitude_', 'elevation_', 'TMAX_', 'TMIN_', 'PRCP_']:
            features[value + str(i)] = []
    with open(os.path.join(measurements_dir, file_name)) as f:
        all_available_stations = json.load(f)
        for station in station_values.keys():
            best_stations = get_best_available_stations(closest_stations[station], all_available_stations)
            for i in range(num_stations):
                for value in ['latitude', 'longitude', 'elevation', 'TMAX', 'TMIN', 'PRCP']:
                    if i < len(best_stations):
                        features[value + '_' + str(i + 1)].append(best_stations[i].get(value))
                    else:
                        features[value + '_' + str(i + 1)].append(None)
    return features

def get_features():
    df = pd.DataFrame()
    files = os.listdir(measurements_dir)
    for file_name in files:
        print('Processing {}'.format(file_name))
        df = df.append(pd.DataFrame(get_features_for_file(file_name)))
    df.to_csv('ProcessedMeasurements.csv')

get_features()
