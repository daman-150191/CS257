import time
import googlemaps # pip install googlemaps
import pandas as pd # pip install pandas

def miles_to_meters(miles):
    try:
        return miles * 1_609.344
    except:
        return 0
        
API_KEY = open('API_KEY.txt', 'r').read()
map_client = googlemaps.Client(API_KEY)

address = '1 Washington Sq, San Jose, CA 95192'
geocode = map_client.geocode(address=address)
(lat, lng) = map(geocode[0]['geometry']['location'].get, ('lat', 'lng'))

search_string = 'parking lot'
distance = miles_to_meters(10)
result = []

response = map_client.places_nearby(
    location=(lat, lng),
    keyword=search_string,
    radius=distance
)   

result.extend(response.get('results'))
next_page_token = response.get('next_page_token')

while next_page_token:
    time.sleep(2)
    response = map_client.places_nearby(
        location=(lat, lng),
        keyword=search_string,
        radius=distance,
        page_token=next_page_token
    )   
    result.extend(response.get('results'))
    next_page_token = response.get('next_page_token')

df = pd.DataFrame(result)
df['url'] = 'https://www.google.com/maps/place/?q=place_id:' + df['place_id']
df.to_excel('{0}.xlsx'.format(search_string), index=False)