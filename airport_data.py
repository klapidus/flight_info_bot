import pandas as pd
import geopy.distance

import settings

def get_airport_coords_by_city(airport_df, city):
    coords = airport_df[(airport_df['municipality'] == city) & (airport_df['type'] == 'large_airport')]['coordinates']
    return coords.values[0] #if more than one airport, return the first one

def get_airport_codes(city):
    if CITY_AIRPORTS_DICT.get(city):
        return CITY_AIRPORTS_DICT[city]['iata_code']

def get_cities_nearby(city):
    #brute force approach for now
    #todo improve with geo queries from a DB?
    cities_nearby = []
    for dest_city in CITY_AIRPORTS_DICT.keys():
        if dest_city == city:
            continue
        est_flight_time = get_flight_time_estimate(city, dest_city)
        if est_flight_time <= settings.FLIGHT_TIME_THRESHOLD:
            cities_nearby.append(dest_city)
    return cities_nearby

def get_flight_time_estimate(city1, city2):
    #emperical value for now, can get it from actual flight times
    #todo would be interesting to plot (distance vs actual flight time)
    #and construct a more realistic estimate
    coords_1 = get_airport_coords_by_city(airport_df, city1)
    coords_2 = get_airport_coords_by_city(airport_df, city2)
    dist = geopy.distance.geodesic(coords_1, coords_2).km
    return dist/settings.PLANE_SPEED #km/h

def create_city_airport_dict(airport_df):
    df = airport_df[airport_df['type'] == 'large_airport'][{'iata_code', 'municipality'}].dropna()
    # https://stackoverflow.com/a/39078846
    return df.groupby('municipality').apply(lambda dfg: dfg.drop('municipality', axis=1).to_dict(orient='list')).to_dict()


#https://github.com/datasets/airport-codes/blob/master/data/airport-codes.csv
airport_df = pd.read_csv('airport-codes.csv')
CITY_AIRPORTS_DICT = create_city_airport_dict(airport_df)
