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
        print('Found closest stations for', id)
    return sorted_stations

closest_stations = get_closest_stations()

def get_best_available_stations(sorted_row, all_available_stations):
    best_available_stations = [[] for i in range(2 * day_span + 1)]
    i = 1
    while i < len(sorted_row) and len(best_available_stations[0]) < num_stations:
        if all([sorted_row[i] in day and 'PRCP' in day[sorted_row[i]] for day in all_available_stations]):
            for day_number in range(2 * day_span + 1):
                best_available_stations[day_number].append(all_available_stations[day_number][sorted_row[i]])
        i += 1
    return best_available_stations

def get_features_for_file(file_name):
    station_values = []
    for i in range(-day_span, day_span + 1):
        with open(os.path.join(get_neighbour(file_name, i))) as f:
            station_values.append(json.load(f))
    features = {value: [station_values[len(station_values) // 2][station].get(value) for station in station_values[len(station_values) // 2]
    if 'PRCP' in station_values[len(station_values) // 2][station]] for value in ['latitude', 'longitude', 'elevation', 'PRCP']}

    for i in range(1, num_stations + 1):
        for value in ['latitude_delta', 'longitude_delta', 'elevation']:
            features[value + '_' + str(i)] = []
        for j in range(1, 2 * day_span + 2):
            features['PRCP_' + str(i) + '_' + str(j)] = []
    for station in station_values[len(station_values) // 2]:
        if not 'PRCP' in station_values[len(station_values) // 2][station]:
            continue
        best_stations = get_best_available_stations(closest_stations[station], station_values)
        for i in range(num_stations):
            if i < len(best_stations[0]):
                features['latitude_delta_' + str(i + 1)].append(best_stations[0][i].get('latitude') - station_values[len(station_values) // 2][station].get('latitude'))
                features['longitude_delta_' + str(i + 1)].append(best_stations[0][i].get('longitude') - station_values[len(station_values) // 2][station].get('longitude'))
                features['elevation_' + str(i + 1)].append(best_stations[0][i].get('elevation'))
                for j in range(2 * day_span + 1):
                    features['PRCP_' + str(i + 1) + '_' + str(j + 1)].append(best_stations[j][i].get('PRCP'))
            else:
                features['latitude_delta_' + str(i + 1)].append(None)
                features['longitude_delta_' + str(i + 1)].append(None)
                features['elevation_' + str(i + 1)].append(None)
                for j in range(2 * day_span + 1):
                    features['PRCP_' + str(i + 1) + '_' + str(j + 1)].append(None)
    features['day'] = [datetime.datetime.strptime(file_name[:-5], '%Y-%m-%d').timetuple().tm_yday] * len(features['latitude'])
    return features

def get_features():
    features = {}
    files = os.listdir(measurements_dir)
    for file_name in files:
        if not fits_with_span(file_name):
            continue
        print('Processing {}'.format(file_name))
        new_features = get_features_for_file(file_name)
        for key in new_features:
            if key in features:
                features[key].extend(new_features[key])
            else:
                features[key] = new_features[key]
    df = pd.DataFrame(features)
    df = df[[value for value in df if value != 'PRCP'] + ['PRCP']]
    df.to_csv('ProcessedMeasurements.csv', index=False)

get_features()
