from math import sin, cos, sqrt, atan2, radians
from pyproj import Transformer
import requests
import csv
class DataUtil:
    def __init__(self):
        lambert = '+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs'
        wgs84 = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
        self.transformer=Transformer.from_crs(lambert, wgs84)

    def findingCoordinates(self,lambert_x,lambert_y):
        '''
        finding coordinates from labert_x and lambert_y
        '''
        return self.transformer.transform(lambert_x,lambert_y)

    def findCity(self,lat,long):
        '''
        finding city from latitude and longitude 
        '''

        url='https://api-adresse.data.gouv.fr/reverse/?lon={}&lat={}'.format(lat,long)
        response = requests.get(url)
        features=response.json()['features']
        if len(features)==0:
            return ''
        city=features[0]['properties']['city']
        return city

    def findLatLongFromAddress(self,lat,long):
        '''
        finding latitude and longitude from address 
        '''
        url='https://api-adresse.data.gouv.fr/reverse/?lon={}&lat={}'.format(long,lat)
        response = requests.get(url)
        features=response.json()['features']
        if len(features)==0:
            return ''
        city=features[0]['properties']['city']
        return city

    def findDistance(self,lat1,long1,lat2,long2):
        '''
        finding the distance from latitude and longitude 
        '''
        R = 6373.0
        lat1,long1=radians(float(lat1)),radians(float(long1))
        lat2,long2=radians(float(lat2)),radians(float(long2))
        dlon = long2 - long1
        dlat = lat2 - lat1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        return distance

    def calculatingClosestPoint(self,lat,long):
        '''
            calculating the closet point from that lat long 
        '''
        distance=float('inf')
        record={}
        df2 = df.copy()
        df2['distance'] = df.apply(lambda x: findDistance(x['latitude'], x['longitude'],lat,long), axis=1)
        df2.sort_values(by=['distance'], ascending=True)
    def processRow(self,row,lat,long):
        '''
            process each row 
        '''
        row_lat=row['latitude']
        row_lon=row['longitude']
        operator=row['Operateur']
        d=self.findDistance(row_lat,row_lon,lat,long)
        result={
                "2G": row["2G"],
                "3G": row["3G"],
                "4G": row["4G"],
                "max_distance": row["max_distance"]
            }
        if d<row['max_distance']:
            result['max_distance']=d
        return result
        

        
    def groupNetworkByCity(self,lat,long,city):
        '''
            finding the operator by the city 
        '''
        response={}
        with open('final_data.csv','r') as r_csvfile:
            dict_reader = csv.DictReader(r_csvfile,delimiter=',')
            for row in dict_reader:
                if row.get('city','') and row['city']==city:
                    row['max_distance']=float('inf')
                    if row['Operateur'] in response:
                        #print('row',row['Operateur'],response)
                        row['max_distance']=response[row['Operateur']]['max_distance']
                    
                    response[row['Operateur']]=self.processRow(row,lat,long)
        return response
    
    def operatorCodes(self):
        '''
            reading and getting the operator codes
        '''
        codes={}
        with open('operator-codes.csv','r') as r_csvfile:
            dict_reader = csv.DictReader(r_csvfile,delimiter=',')
            for row in dict_reader:
                codes[row['code']]=row['operator']
        return codes
    
    def addressFinder(self,address):
        '''
            finding the address and also entry point from app.py
        '''
        address=address.split()
        address='+'.join(address)
        url='https://api-adresse.data.gouv.fr/search/?q={}'.format(address)
        print('url',url)
        response = requests.get(url)
        features=response.json()['features']
        if len(features)==0:
            return {},"address is not valid"
        a_lat,a_long=response.json()['features'][0]['geometry']['coordinates']
        city=self.findCity(a_lat,a_long)
        if not city:
            return {},"address is valid but cannot find city associated to this city"
        
        results=self.groupNetworkByCity(a_lat,a_long,city)
        #print('results',results)
        codes=self.operatorCodes()
        #print('codes',codes)
        output={}
        for code in results:
             del results[code]['max_distance']
             output[codes[code]]=results[code]
        return output,""
