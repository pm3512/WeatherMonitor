import json
import requests
import json_flatten

tokens = ['pQjpjnuowebqoRHjvgJfhSnSvRPlxlJt', 'mJIjDxRUCQJDpXIEiwpJfKNxhZgrYGvx']
token_number = 0

parameters = {
        'token': tokens[token_number]
        }

keys = {
        'results.0.value$int': 'precipitation',
        'results.0.value$float': 'precipitation'
        }
    
def change_token():
    global token_number
    token_number += 1
    if(token_number == len(tokens)):
        token_number = 0

def get_raw_weather(id, start_date, end_date):
    
    return requests.get('https://www.ncdc.noaa.gov/cdo-web/api/v2/data?datasetid=GHCND&stationid=' + 
                               id + '&startdate=' + start_date + 
                               '&enddate=' + end_date, headers = parameters)
    
def get_weather(station, start_date, end_date):
    global token_number
    global parameters
    raw_weather = get_raw_weather(station[0], start_date, end_date)
    while raw_weather.status_code == 429:
        change_token()
        parameters['token'] = tokens[token_number]
        raw_weather = get_raw_weather(station[0], start_date, end_date)
    raw_weather = json_flatten.flatten(raw_weather.json())
    processed_weather = dict.fromkeys([keys[key] for key in keys])
    for key in keys:
        if key in raw_weather:
            processed_weather[keys[key]] = raw_weather[key]
    processed_weather['id'] = station[0]
    processed_weather['latitude'] = station[1]
    processed_weather['longitude'] = station[2]
    return processed_weather

def get_all_data(date):
    with open('StationsForMeasurement.txt', 'r') as read_file:
        stations = read_file.read().splitlines()
        with open('./Measurements/' + date + '.json', 'w') as write_file:
            write_file.truncate(0)
            counter = 0
            for station in stations:
                counter += 1
                if counter % 200 == 0:
                    print(str(round(min(counter / len(stations) * 100, 100), 1)) + "% complete")
                try:
                    weather = get_weather(station.split(" "), date, date)
                    print(weather['precipitation'])
                    print(weather['precipitation'] != None)
                    if weather['precipitation'] != None:
                        json.dump(weather, write_file)
                        write_file.write('\n')
                except Exception as e:
                    print(e)
                    if type(e) == KeyboardInterrupt:
                        exit()
                    print("Couldn't process " + station)
            write_file.close()
        read_file.close()

get_all_data('2019-02-25')