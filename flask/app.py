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

      print(addresses, algorithm, centroid, method)

      # centroid is an option parameters
      if (
         not addresses or
         not algorithm or
         not method
      ):
         return render_template("form.html")

      POIs = get_POIs_latlng(addresses)
      input_coords = POIs

      if centroid:
         if centroid == 'avg':
            POIs = get_centroid_avg(POIs)
         elif centroid == 'avg_start_end':
            POIs = get_centroid_avg_start_end(POIs)

      pklots_latlng, pklots_metadata, pklots_latlng2name = get_pklots_latlng()

      closest_pklot = None
      if algorithm == 'p2point':
         closest_pklot = get_closest_parking_p2point(method, POIs, pklots_latlng)
      elif algorithm == 'p2poly':
         closest_pklot = get_closest_parking_p2poly(POIs[0], pklots_latlng)

      print("Closest parking: {} - {}".format(
         pklots_latlng2name[(
            closest_pklot['lat'],
            closest_pklot['lng']
         )],
         closest_pklot,
      ))

    gmap = gmplot.GoogleMapPlotter(closest_pklot['lat'], closest_pklot['lng'], 13)

    # Extract the latitudes and longitudes from the input data
    lats = [coord['lat'] for coord in input_coords]
    lngs = [coord['lng'] for coord in input_coords]

    # Add the input points to the map
    gmap.scatter(lats, lngs, c='r', marker=True)
    gmap.scatter([float(closest_pklot['lat'])], [float(closest_pklot['lng'])], c='b', marker=True)

    gmap.draw('templates/map1.html')

    # Render the HTML file in the Flask app
    return render_template('map1.html')


if __name__=='__main__':
   app.run(debug=False)