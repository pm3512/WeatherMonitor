import requests
import json

token = 'pQjpjnuowebqoRHjvgJfhSnSvRPlxlJt'

batch_size = 1000

areas = [[45, 0, 57, 22]]


def check_position(lat, lon):
    for area in areas:
        if area[0] < lat < area[2] and area[1] < lon < area[3]:
            return True
    return False


offset = 0
with open('StationsForMeasurement.json', 'w') as f:
    f.truncate(0)
    data = []
    print(json.loads(requests.get('https://www.ncdc.noaa.gov/cdo-web/api/v2/stations?limit=1000', headers={'token': token}).text))
    while True:
        stations = requests.get('https://www.ncdc.noaa.gov/cdo-web/api/v2/stations?limit=' + str(
            batch_size) + '&offset=' + str(offset), headers={'token': token})
        if(stations.status_code != 200):
            print("Something went wrong, code {}".format(stations.status_code))
            f.close()
            exit()
        stations = json.loads(stations.text)
        if stations == {}:
            break
        for station in stations['results']:
            if 'ALL' in areas or check_position(station['latitude'], station['longitude']):
                data.append({'id': station['id'], 'lattitude': station['latitude'], 'longitude': station['longitude'], 'elevation': station['elevation']})
        offset += batch_size
        print(str(round(min(
            offset / stations['metadata']['resultset']['count'] * 100, 100), 1)) + "% complete")
    json.dump(data, f, indent=2)
    f.close()
