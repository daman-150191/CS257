from flask import Flask, request, render_template
 
app = Flask(__name__)  
 
@app.route('/', methods =["GET", "POST"])
def find_parking():
    if request.method == "POST":
       data = request.form
       print(data)
       
    return render_template("form.html")
 
if __name__=='__main__':
   app.run(debug=False)