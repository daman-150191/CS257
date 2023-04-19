import json
import math
from geopy import Nominatim
import argparse
import pandas as pd
from collections import defaultdict
from math import radians, cos, sin, asin, sqrt

def get_POIs_latlng(addresses):
    POIs = []
    for idx, address in enumerate(addresses):
        locator = Nominatim(user_agent="myGeocoder")
        location = locator.geocode(address)
        if not location:
            print("[Error] Coordinates can't be found for {}".format(address))
            continue
        print("POI({}): {}\n{}\n".format(
            idx, 
            address.strip(),
            {
                'lat' : location.latitude,
                'lng' : location.longitude,
            } 
        )) 
        POIs.append(
            {
                'lat' : location.latitude,
                'lng' : location.longitude,
            }
        )
    
    return POIs

def get_POIs_latlng_from_file(filename = "../data/POIs.txt"):
    POIs = []
    with open(filename) as fptr:
        addresses = fptr.readlines()
        for idx, address in enumerate(addresses):
            locator = Nominatim(user_agent="myGeocoder")
            location = locator.geocode(address.strip())
            if not location:
                print("[Error] Coordinates can't be found for {}".format(address))
                continue
            print("POI({}): {}\n{}\n".format(
                idx, 
                address.strip(),
                {
                    'lat' : location.latitude,
                    'lng' : location.longitude,
                } 
            )) 
            POIs.append(
                {
                    'lat' : location.latitude,
                    'lng' : location.longitude,
                }
            )

    return POIs


def get_pklots_latlng():
    df = pd.read_excel('../data/parking_lot.xlsx')
    pklots_geometry = df['geometry'].to_list()
    pklots_name = df['name'].to_list()

    pklots_latlng, pklots_latlng2name = [], defaultdict(str)
    for pklot_geometry, pklot_name in zip(pklots_geometry, pklots_name):
        pklot_geometry = json.loads(pklot_geometry.replace("'", '"'))
        pklots_latlng.append(pklot_geometry['location'])
        pklots_latlng2name[ 
            (
                pklot_geometry['location']['lat'], 
                pklot_geometry['location']['lng']
            ) 
        ] = pklot_name
    
    return pklots_latlng, pklots_latlng2name

def get_closest_parking_p2poly(centroid, lots):
    INF = float('inf')
    min_dist, closest_pklot = INF, lots[0]
    for pklot in lots:
        dist = math.dist([centroid['lat'], centroid['lng']], [pklot['lat'], pklot['lng']])
        if dist < min_dist:
            min_dist = dist
            closest_pklot = pklot

    return closest_pklot

def get_closest_parking_p2point(method, coords, lots):
    INF = float('inf')
    min_dist, closest_pklot = INF, lots[0]
    for pklot in lots:
        dist = 0
        for coord in coords:
            if method == 'euc': dist += math.dist([coord['lat'], coord['lng']], [pklot['lat'], pklot['lng']])
            else: dist += haversine_dist(coord['lat'], coord['lng'], pklot['lat'], pklot['lng'])
        if dist < min_dist:
            min_dist = dist
            closest_pklot = pklot

    return closest_pklot

def haversine_dist(lat_0, lon_0, lat_1, lon_1):
      R = 3959.87433 
      return (3959.87433 * 2*asin(sqrt(sin(radians(lat_1 - lat_0)/2)**2 + 
                cos(radians(lat_0))*cos(radians(lat_1))*sin(radians(lon_1 - lon_0)/2)**2)))

def get_centroid_avg_start_end(POIs, start_idx=0, end_idx=-1):
    INF = float('inf')
    size = len(POIs)
    if size == 0:
        return {'lat': INF, 'lng': INF}

    avg_lat = (
        POIs[start_idx]['lat'] +
        POIs[end_idx]['lat'] 
    ) / 2
    
    avg_lng = (
        POIs[start_idx]['lng'] +
        POIs[end_idx]['lng'] 
    ) / 2

    return [{
        'lat' : avg_lat,
        'lng' : avg_lng,
    }]
    
def get_centroid_avg(POIs):
    INF = float('inf')
    size = len(POIs)
    if size == 0:
        return {'lat' : INF, 'lng' : INF}

    avg_lat, avg_lng = 0.0, 0.0
    for POI in POIs:
        avg_lat += POI['lat']
        avg_lng += POI['lng']

    avg_lat /= size
    avg_lng /= size

    return [{
        'lat' : avg_lat,
        'lng' : avg_lng,
    }]

def main():
    parser = argparse.ArgumentParser(
        description="Find the name and coordinate of the nearest parking lot given a list of POIs"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-p', '--polygon', 
        nargs="+", 
        help='Specify POI(s) with 1+ of coordinates with the format of \"LAT,LNG\", where comma separate latitude and longitude of each coordinate tuple',
    )
    group.add_argument(
        '-f', '--filename',
        help="Read a list of POIs from file with each POI a separate line of physical address"
    )
    parser.add_argument(
        '-c', '--centroid', 
        choices=['avg', 'avg_start_end'],
        help="Algorithms to abstract a list of POIs into a centroid node"
    )
    parser.add_argument(
        '-a', '--algorithm', 
        choices=['p2point', 'p2poly'],
        required=True,
        help="Algorithms to measure the distance"
    )
    parser.add_argument(
        '-m', '--method',
        choices=['euc', 'hav'],
        required=True,
        help="Distance calculation methods for point-to-point approach"
    )
    args = parser.parse_args()
    
    POIs = [
        {'lat' : float(lat), 'lng' : float(lng)}
        for lat, lng in (coord.split(',') for coord in args.polygon)
    ] if args.polygon else get_POIs_latlng_from_file(args.filename)

    if args.centroid:
        if args.centroid == 'avg':
            POIs = get_centroid_avg(POIs)
        elif args.centroid == 'avg_start_end':
            POIs = get_centroid_avg_start_end(POIs)

    pklots_latlng, pklots_latlng2name = get_pklots_latlng()
    
    closest_pklot = None
    if args.algorithm == 'p2point':
        closest_pklot = get_closest_parking_p2point(args.method, POIs, pklots_latlng)
    elif args.algorithm == 'p2poly':
        closest_pklot = get_closest_parking_p2poly(POIs[0], pklots_latlng)
        

    print("Closest parking: {} - {}".format(
        pklots_latlng2name[(
            closest_pklot['lat'],
            closest_pklot['lng']
        )],
        closest_pklot,
    ))

if __name__ == '__main__':
    main()