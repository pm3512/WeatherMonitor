import json
import requests
import os
from dotenv import load_dotenv
import datetime

load_dotenv()

batch_size = 130


def get_raw_weather(ids, start_date, end_date):
    request_ids = '&stationid='.join(id for id in ids)
    return requests.get('https://www.ncdc.noaa.gov/cdo-web/api/v2/data?datasetid=GHCND&stationid=' + request_ids +
                        '&startdate=' + start_date + '&enddate=' + end_date + '&limit=1000', headers={'token': os.getenv('NOAA_TOKEN')})


def get_weather(stations, start_date, end_date):
    raw_weather = get_raw_weather([station['id'] for station in stations], start_date, end_date)
    if raw_weather.status_code == 429:
        print('No requests left!')
        return None
    if raw_weather.status_code != 200:
        print('Some problems, status code {}'.format(raw_weather.status_code))
        return None
    raw_weather = raw_weather.json()
    if(raw_weather == {}):
        return {}
    processed_weather = {station['id']: {'latitude': station['latitude'], 'longitude': station['longitude'], 'elevation': station['elevation']} for station in stations}
    for measurement in raw_weather['results']:
        processed_weather[measurement['station']][measurement['datatype']] = measurement['value']
    return {station: measurements for station, measurements in processed_weather.items() if len(measurements) > 3}


def get_weather_for_all_stations(date):
    offset = 0
    all_weather = {}
    with open('StationsForMeasurement.json', 'r') as read_file:
        stations = json.load(read_file)
        with open('Measurements/' + date + '.json', 'w') as write_file:
            write_file.truncate(0)
            while offset < len(stations):
                try:
                    weather = get_weather(stations[offset: offset + batch_size], date, date)
                    if weather == None:
                        return False
                    all_weather.update(weather)
                except Exception as e:
                    print(e)
                    if type(e) == KeyboardInterrupt:
                        exit()
                offset += batch_size
                print(str(round(min(offset / len(stations) * 100, 100), 1)) + "% complete")
            json.dump(all_weather, write_file, indent=2)
            write_file.close()
        read_file.close()
    return True


def get_weather_ALAP(start_date):
    can_get_more = True
    cur_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    while can_get_more:
        print('Processing ' + cur_date.strftime('%Y-%m-%d'))
        can_get_more = get_weather_for_all_stations(cur_date.strftime('%Y-%m-%d'))
        cur_date += datetime.timedelta(days=-1)

#get_weather_ALAP('2018-06-17')