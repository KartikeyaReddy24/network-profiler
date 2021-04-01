import requests
from flask import *

import pandas as pd
import io
import csv
from pyproj import Transformer
from data import DataUtil

app = Flask(__name__)
app.config["DEBUG"] = True
data=DataUtil()

@app.route('/api', methods=['GET'])
def home():
    address = request.args.get('q')
    body,error=data.addressFinder(address)
    
    return jsonify(body)
    

app.run()