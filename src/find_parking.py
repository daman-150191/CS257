import json
import math
import argparse
import pandas as pd
from collections import defaultdict

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

def get_closest_parking_p2point(coords, lots):
    INF = float('inf')
    min_dist, closest_pklot = INF, lots[0]
    for pklot in lots:
        dist = 0
        for coord in coords:
            dist += math.dist([coord['lat'], coord['lng']], [pklot['lat'], pklot['lng']])
        if dist < min_dist:
            min_dist = dist
            closest_pklot = pklot

    return closest_pklot

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
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--polygon', nargs="+")
    parser.add_argument('-c', '--centroid', choices=['avg', 'avg_start_end'])
    parser.add_argument('-a', '--algorithm', choices=['p2point', 'p2poly'], required=True)
    args = parser.parse_args()
    
    default_POIs = [
        {'lat': 37.392109, 'lng': -122.038797},
        {'lat': 37.387970, 'lng': -122.020247},
        {'lat': 37.372724, 'lng': -122.014402},
        {'lat': 37.363737, 'lng': -122.033207},
        {'lat': 37.381869, 'lng': -122.043106},
    ]
    POIs = default_POIs if args.polygon == None else [
        {'lat' : float(lat), 'lng' : float(lng)}
        for lat, lng in (coord.split(',') for coord in args.polygon)
    ]

    pklots_latlng, pklots_latlng2name = get_pklots_latlng()

    if args.centroid:
        if args.centroid == 'avg':
            POIs = get_centroid_avg(POIs)
        elif args.centroid == 'avg_start_end':
            POIs = get_centroid_avg_start_end(POIs)
    
    closest_pklot = None
    if args.algorithm == 'p2point':
        closest_pklot = get_closest_parking_p2point(POIs, pklots_latlng)
    elif args.algorithm == 'p2poly':
        closest_pklot = get_closest_parking_p2poly(POIs[0], pklots_latlng)

    print("{} - {}".format(
        pklots_latlng2name[(
            closest_pklot['lat'],
            closest_pklot['lng']
        )],
        closest_pklot,
    ))

if __name__ == '__main__':
    main()
