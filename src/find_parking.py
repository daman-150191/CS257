import json
import pandas as pd

def get_parking_lots_lat_lng():
    df = pd.read_excel('../data/parking_lot.xlsx')
    parking_lots = df['geometry'].to_list()

    parking_lots_lat_lng = []
    for parking_lot in parking_lots:
        parking_lot_geometry = json.loads(parking_lot.replace("'", '"'))
        parking_lots_lat_lng.append(parking_lot_geometry['location'])
    
    return parking_lots_lat_lng

def get_closest_parking_lot_lat_lng(centroid, parking_lots_lat_lng):
    INF = float('inf')
    centroid_lat, centroid_lng = centroid['lat'], centroid['lng']
    min_dist, closest_parking_lot_lat_lng = INF, None
    for parking_lot_lat_lng in parking_lots_lat_lng:
        parking_lot_lat, parking_lot_lng = parking_lot_lat_lng['lat'], parking_lot_lat_lng['lng']
        dist = (centroid_lat - parking_lot_lat) ** 2 + (centroid_lng - parking_lot_lng) ** 2
        if dist < min_dist:
            min_dist = dist
            closest_parking_lot_lat_lng = parking_lot_lat_lng

    return closest_parking_lot_lat_lng

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

    return {
        'lat' : avg_lat,
        'lng' : avg_lng,
    }
    
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

    return {
        'lat' : avg_lat,
        'lng' : avg_lng,
    }

def main():
    parking_lots_lat_lng = get_parking_lots_lat_lng()
    POIs = [
        {'lat': 37.392109, 'lng': -122.038797},
        {'lat': 37.387970, 'lng': -122.020247},
        {'lat': 37.372724, 'lng': -122.014402},
        {'lat': 37.363737, 'lng': -122.033207},
        {'lat': 37.381869, 'lng': -122.043106},
    ]

    centroid = get_centroid_avg(POIs)
    closest_parking_lot_lat_lng = get_closest_parking_lot_lat_lng(centroid, parking_lots_lat_lng)
    print(closest_parking_lot_lat_lng)

    centroid = get_centroid_avg_start_end(POIs)
    closest_parking_lot_lat_lng = get_closest_parking_lot_lat_lng(centroid, parking_lots_lat_lng)
    print(closest_parking_lot_lat_lng)


if __name__ == '__main__':
    main()