import sys
sys.path.append("../src")
from gmplot import gmplot

from flask import Flask, request, render_template
from find_parking import *

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('form.html')

@app.route('/find', methods =["GET", "POST"])
def find_parking():
   if request.method == "POST":
      addresses = request.form.getlist("addresses")
      algorithm = request.form.get("algorithm")
      centroid = request.form.get("centroid")
      method = request.form.get("method")

      # centroid is an option parameters
      if (
         not addresses or
         not algorithm or
         (algorithm == 'p2poly' and not method)
      ):
         return render_template("form.html")
      
      pklots_latlng, pklots_metadata, pklots_latlng2name = get_pklots_latlng()
      POIs = get_POIs_latlng_from_gmap(addresses)

      centroid_POI = None
      if centroid:
         if centroid == 'avg':
            centroid_POI = get_centroid_avg(POIs)[0]
         elif centroid == 'avg_start_end':
            centroid_POI = get_centroid_avg_start_end(POIs)[0]

      closest_pklot = None
      if algorithm == 'p2point':
         if centroid:
            closest_pklot= get_closest_parking_p2point(method, [centroid_POI], pklots_latlng)
         else:
            closest_pklot = get_closest_parking_p2point(method, POIs, pklots_latlng)
      elif algorithm == 'p2poly':
         if not centroid_POI:
            centroid_POI = POIs[0]
            print('[Warning] Algorithm p2poly (Point to Polygon) should pass in an centroid')
         closest_pklot = get_closest_parking_p2poly(centroid_POI, pklots_latlng)

   gmap = gmplot.GoogleMapPlotter(closest_pklot['lat'], closest_pklot['lng'], 13, apikey=open('API_KEY.txt', 'r').read())

   # Add all other parking lots
   gmap.scatter(
      [pklot_latlng['lat'] for pklot_latlng in pklots_latlng],
      [pklot_latlng['lng'] for pklot_latlng in pklots_latlng],
      color = 'grey',
      marker = True,
      size = 20,
      title = [
         pklots_latlng2name[(
            pklot_latlng['lat'],
            pklot_latlng['lng']
         )]
         for pklot_latlng in pklots_latlng
      ]    
   )

   # Add centroid to map
   if centroid:
      gmap.scatter(
         [centroid_POI['lat']], 
         [centroid_POI['lng']], 
         color = 'green', 
         marker = True,
         title = "Centroid"
      )

    # Add POIs to map
   gmap.scatter(
      [POI['lat'] for POI in POIs], 
      [POI['lng'] for POI in POIs], 
      color = 'r',
      marker = True, 
      title = [
         address
         for address in addresses
      ]
   )

   # Add closest parking lot
   gmap.scatter(
      [closest_pklot['lat']], 
      [closest_pklot['lng']], 
      color = 'b', 
      marker = True,
      title = pklots_latlng2name[(
         closest_pklot['lat'],
         closest_pklot['lng']
      )]
   )

   gmap.polygon(
      [POI['lat'] for POI in POIs],
      [POI['lng'] for POI in POIs],
      edge_color='cornflowerblue',
      edge_width=5
   )

   gmap.draw('templates/google_map.html')

   # Render the HTML file in the Flask app
   return render_template('google_map.html')


if __name__=='__main__':
   app.run(debug=False)
