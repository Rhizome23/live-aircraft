import pandas as pd
from opensky_api import OpenSkyApi
import time
import requests


def get_flight_data(area):
   start = time.time()
   # bboxFrance= [min_latitude, max_latitude, min_longitude, max_longitude]
   bboxdict = {'FRANCE': [41, 52, -5.5, 10], 'EUROPE': [37, 65, -10, 25], 'NA': [26, 60, -125, -63]}
   if area in bboxdict:
       bbox = bboxdict[area]

   t = int(time.time())

   #  fly data
   data = []
   api = OpenSkyApi()
   try:
      states = api.get_states(time_secs=t, bbox=bbox)
      if states is not None:
         for s in states.states:
           if s.latitude is not None and s.longitude is not None:
         #print("(%r, %r, %r, %r)" % (s.longitude, s.latitude, s.velocity, s.callsign))
      # print(s)
             data.append((s.latitude, s.longitude, s.velocity, s.callsign, s.origin_country, s.baro_altitude, s.icao24))
   except requests.exceptions.ReadTimeout:
      pass
        

   df = pd.DataFrame(data, columns=['Lat', 'Long', 'Velocity','Callsign', 'From', 'Altitude', 'Icao24'])
   flight_df = df.fillna('No Data')  # replace NAN with No Data
   df['Velocity'].mask(df['Velocity'] == 'No Data', 0, inplace=True)

   # We add Airlines name and Aircraft Model to our dataframe
   df_airlines = pd.read_csv("data/airlines.dat",
                            names=['id', 'name', 'alias', 'iata', 'icao', 'callsign', 'country', 'active'])
   #df_aircraft = pd.read_csv("data/aircraftDatabase.csv", low_memory=False)
   flight_df['Airlines_name'] = flight_df['Callsign'].apply(lambda x: x[0:3])

   #flight_df["Aircraft_model"] = flight_df['Icao24']
   a = df_airlines.set_index('icao')['name']
   flight_df["Airlines_name"] = flight_df["Airlines_name"].replace(a)

   #b = df_aircraft.set_index('icao24')['typecode']
   #flight_df["Aircraft_model"] = flight_df["Aircraft_model"].replace(b)

   flight_df['Velocity'] = flight_df['Velocity'].apply(lambda x: x*3,6)


   #print(flight_df.head())
   end = time.time()
   #print("temps d'exécution en sec :", int(end-start))
   
   return flight_df



