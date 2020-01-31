from itertools import product

import pandas as pd
import geopy.distance

def get_airport_coords_by_city(airport_df, city):
    coords = airport_df[(airport_df['municipality'] == city) & (airport_df['type'] == 'large_airport')]['coordinates']
    return coords.values[0] #if more than one airport, return the first one


def get_airport_codes(city):
    if city in CITY_AIRPORTS_DICT:
        return CITY_AIRPORTS_DICT[city]['iata_code']


def get_cities_nearby(city, max_dist):
    #brute force approach for now
    #todo improve with geo queries from a DB?
    cities_nearby = []
    for dest_city in CITY_AIRPORTS_DICT.keys():
        if dest_city == city:
            continue
        if get_distance(city, dest_city) <= max_dist:
            cities_nearby.append(dest_city)
    return cities_nearby


def get_distance(city1: str, city2: str) -> float:
    coords_1 = get_airport_coords_by_city(airport_df, city1)
    coords_2 = get_airport_coords_by_city(airport_df, city2)
    return geopy.distance.geodesic(coords_1, coords_2).km


def create_city_airport_dict(airport_df):
    df = airport_df[airport_df['type'] == 'large_airport'][{'iata_code', 'municipality'}].dropna()
    # https://stackoverflow.com/a/39078846
    return df.groupby('municipality').apply(lambda dfg: dfg.drop('municipality', axis=1).to_dict(orient='list')).to_dict()


#https://github.com/datasets/airport-codes/blob/master/data/airport-codes.csv
airport_df = pd.read_csv('airport-codes.csv')
CITY_AIRPORTS_DICT = create_city_airport_dict(airport_df)