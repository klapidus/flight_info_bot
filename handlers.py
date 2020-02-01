from itertools import product
import random
import time

import datetime

from airport_data import get_cities_nearby, get_airport_codes, get_distance
from db import db, insert_flights_to_db, find_flights_from_db, insert_na_flight_to_db, is_na_flight_in_db
import settings
from utils import get_weekend_days
from weather import is_good_weekend_weather


def find_connections_from_db_or_api(db, api, origin, destination, dep_date):

    #first check non-available flights from a dedicated collection in the db
    if is_na_flight_in_db(db, origin, destination, dep_date):
        return None

    # first from db, then from api
    flights = find_flights_from_db(db, origin, destination, dep_date)
    print('db', len(flights))
    if not flights:
        flights = api.find_connections(origin, destination, dep_date)
        if flights:
            print('api', len(flights))
            #not in the db, add to the db
            insert_flights_to_db(db, flights)
        else:
            #special collection in the db: API was asked, but no flights were found
            #might re-check them again (API request error) or they are genuingly not available
            insert_na_flight_to_db(db, origin, destination, dep_date)
    return flights


def printout_flights(bot, update, flights):
    for idx, flight in enumerate(flights, 1):
        fl_dep = flight.departure_datetime.strftime("%H:%M")
        fl_arr = flight.arrival_datetime.strftime("%H:%M")
        fl_dur_h, fl_dur_m = divmod(flight.duration, 60)
        update.message.reply_text(f'{idx}. {flight.airline_id}{flight.flight_number}, {fl_dep}-{fl_arr}, {fl_dur_h}h {fl_dur_m}min',
                                  parse_mode='Markdown')


def find_flight(bot, update, api):
    in_text = update.message.text
    _, cities, dep_date = in_text.split()
    start_city, goal_city = cities.split('-')
    try:
        dep_date = datetime.datetime.strptime(dep_date, '%d-%m-%Y')
    except ValueError:
        update.message.reply_text('The departure date is not valid!')

    start_airports = get_airport_codes(start_city)
    goal_airports = get_airport_codes(goal_city)

    flight_found = False
    for a1, a2 in product(start_airports, goal_airports):
        flights = find_connections_from_db_or_api(db, api, a1, a2, dep_date.date())
        if flights:
            flight_found = True
            update.message.reply_text(f'{len(flights)} flights found from {start_city} ({a1}) to {goal_city} ({a2}):')
            printout_flights(bot, update, flights)

    if not flight_found:
        update.message.reply_text('No connections found!')
    else:
        update.message.reply_text('Search completed.')



def weekend_trip(bot, update, api):

    in_text = update.message.text
    try:
        start_city = in_text.split()[1]
    except IndexError:
        start_city = 'Moscow'  #DEFAULT CITY

    try:
        max_dist = int(in_text.split()[2])
    except IndexError:
        max_dist = settings.MAX_DIST  #DEFAULT MAX DIST

    #check if there is an airport in the chosen starting city
    #multiple airports in a large city
    start_airports = get_airport_codes(start_city)
    if start_airports is None:
        print('No airport found in the chosen city!')
        update.message.reply_text('No airport found in the chosen city! Choose another starting city!')
        return False

    #find cities (from a dict of cities with airports) within max_dist
    cities_nearby = get_cities_nearby(start_city, max_dist)
    print(cities_nearby)
    if cities_nearby:
        update.message.reply_text(f'Possible destinations within {max_dist} km: ' + ', '.join(cities_nearby))
    else:
        update.message.reply_text(f'No major airports found within {max_dist} km!')

    #find next weekend dates:
    friday, saturday, sunday = get_weekend_days()

    #select only cities with good weather forecast on next Saturday
    # cities_nearby_good_weather = [city for city in cities_nearby if is_good_weekend_weather(city, saturday)]
    # this below doesn't work?
    # cities_nearby_good_weather = list(filter(lambda x: filter_good_weekend_weather(x, saturday), cities_nearby))
    # print(cities_nearby_good_weather)
    # if not cities_nearby_good_weather:
    #     update.message.reply_text('No city with a decent weather found!')

    trip_found = False
    # for city in cities_nearby_good_weather: #disabled for now
    for city in cities_nearby:
        print(start_city, city)

        airports = get_airport_codes(city)
        if airports is None:
            continue

        for airport1, airport2 in product(start_airports, airports):
            print(airport1, airport2)
            flights_forth = find_connections_from_db_or_api(db, api, airport1, airport2, friday)
            if not flights_forth:
                continue
            flights_back = find_connections_from_db_or_api(db, api, airport2, airport1, sunday)
            if flights_back:
                dist = int(get_distance(start_city, city))
                update.message.reply_text(f'*Weekend trip options from {start_city} to {city} (~{dist} km):*',
                                          parse_mode='Markdown')
                trip_found = True

                update.message.reply_text(f'{len(flights_forth)} flights found from {start_city} ({airport1}) to {city} ({airport2}) next Friday')
                printout_flights(bot, update, flights_forth) #todo if too many, return latest flights

                update.message.reply_text(f'{len(flights_back)} flights found from {city} ({airport2}) to {start_city} ({airport1}) next Sunday')
                printout_flights(bot, update, flights_back)

    if not trip_found:
        update.message.reply_text('No weekend trip found! Increase the search distance or change the start city!')
    else:
        update.message.reply_text('Search for a weekend trip is completed.')


def start(bot, update):
        update.message.reply_text(
            'Find a flight: /find_flight Moscow-London DD-MM-YYY\n'
            'Find a weekend trip: /weekend_trip [CITY] [DISTANCE]}')
