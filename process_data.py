
import flask
import pandas as pd
import io
import csv
from data import DataUtil 
import requests

def process_data():
    dutil= DataUtil()
    with open('2018_01_Sites_mobiles_2G_3G_4G_France_metropolitaine_L93.csv','r') as r_csvfile:
        with open('data.csv','w',newline='') as w_csvfile:
            dict_reader = csv.DictReader(r_csvfile,delimiter=';')
            fieldnames = dict_reader.fieldnames + ['latitude','longitude']
            writer_csv = csv.DictWriter(w_csvfile,fieldnames,delimiter=',')
            writer_csv.writeheader()
            count=0
            for row in dict_reader:
                if row['X'].isnumeric() and row['Y'].isnumeric():
                    longitude,latitude=dutil.findingCoordinates(row['X'],row['Y'])
                    row['latitude'],row['longitude']=latitude,longitude
                    writer_csv.writerow(row)

    csv_with_lat_long_cols = pd.read_csv('data.csv', usecols=['latitude', 'longitude'])
    csv_with_lat_long_cols.to_csv('reverse.csv',index=False,header=True)

    # after we generate the data in reverse.csv
    # we need to do the data processing in two parts 
    # load 38K records each time and load the data into the actual data.csv file

    # curl -X POST -F data=@reverse.csv https://api-adresse.data.gouv.fr/reverse/csv/ >> temp1_with_40K_records.csv
    # curl -X POST -F data=@reverse.csv https://api-adresse.data.gouv.fr/reverse/csv/ >> temp2_with_40K_records.csv

    # city column from the temp file and append it to the data.csv
    
    # final data is stored in final_data.csv
    

process_data()