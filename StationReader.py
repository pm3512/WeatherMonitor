import requests
import json

token = 'pQjpjnuowebqoRHjvgJfhSnSvRPlxlJt'

batch_size = 1000

areas = ['ALL']

parameters = {
        'token': token
        }
 
def check_position(lat, lon):
    for area in areas:
        if area[0] < lat < area[2] and area[1] < lon < area[3]:
            return True
    return False

offset = 0
with open('StationsForMeasurement.txt', 'w') as f:
    print(1)
    f.truncate(0)
    while True:
        stations = requests.get('https://www.ncdc.noaa.gov/cdo-web/api/v2/stations?limit=' + 
                                str(batch_size) + '&offset=' + str(offset), headers = parameters)
        print(2)
        stations = json.loads(stations.text)
        if stations == {}:
            break
        stations = stations['results']
        for station in stations:
            if 'ALL' in areas or check_position(station['latitude'], station['longitude']):
                f.write("{0} {1} {2}\n".format(station['id'], station['latitude'], station['longitude']))
        offset += batch_size
        print(str(round(min(offset / 139464 * 100, 100), 1)) + "% complete")
    f.close()