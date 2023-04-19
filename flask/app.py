import sys
sys.path.append("../src")

from flask import Flask, request, render_template
from find_parking import *
 
app = Flask(__name__)  
 
@app.route('/', methods =["GET", "POST"])
def find_parking():
    if request.method == "POST":
       addresses = request.form.getlist("addresses")
       get_POIs_latlng(addresses)

    return render_template("form.html")
 
if __name__=='__main__':
   app.run(debug=False)