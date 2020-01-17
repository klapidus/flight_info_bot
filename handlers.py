from itertools import product

from airport_data import get_cities_nearby, get_airport_codes
from utils import get_weekend_days
from weather import filter_good_weekend_weather

def printout_flights(bot, update, flights):
    for idx, flight in enumerate(flights, 1):
        update.message.reply_text(f'{idx}: {flight.airline_id}{flight.flight_number}')
        update.message.reply_text(f'Departure: {flight.departure_time.strftime("%H:%M")}')
        update.message.reply_text(f'Arrival: {flight.arrival_time.strftime("%H:%M")}')
        update.message.reply_text(f'Flight duration: {flight.duration} minutes')

def find_flight(bot, update, api):
    in_text = update.message.text
    origin, destination = in_text.split()[1][:3], in_text.split()[1][4:]
    date_time = in_text.split()[2]
    flights = api.find_connections(origin, destination, date_time)
    if flights:
        update.message.reply_text(f'{len(flights)} flights found')
        printout_flights(bot, update, flights)

def weekend_trip(bot, update, api):

    in_text = update.message.text
    try:
        start_city = in_text.split()[1]
    except IndexError:
        start_city = 'Moscow'  #DEFAULT CITY

    #check if there is an airport in the chosen starting city
    #multiple airports in a large city
    start_airports = get_airport_codes(start_city)
    if start_airports is None:
        print('No airport found in the chosen city!')
        update.message.reply_text('No airport found in the chosen city! Choose another starting city!')
        return False

    #find cities (from a dict of cities with airports) 'nearby', <3-4 hours flights
    cities_nearby = get_cities_nearby(start_city)
    print(cities_nearby)

    #find next weekend dates:
    friday, saturday, sunday = get_weekend_days()

    #select only cities with good weather forecast on next Saturday
    cities_nearby_good_weather = [city for city in cities_nearby if filter_good_weekend_weather(city, saturday)]
    # this below doesn't work?
    # cities_nearby_good_weather = list(filter(lambda x: filter_good_weekend_weather(x, saturday), cities_nearby))
    print(cities_nearby_good_weather)

    for city in cities_nearby_good_weather:

        airports = get_airport_codes(city)
        if airports is None:
            continue
        print(airports)

        update.message.reply_text(f'Weekend trip from {start_city} to {city}:')
        for airport1, airport2 in product(start_airports, airports):
            flights = api.find_connections(airport1, airport2, friday)
            if flights:
                update.message.reply_text(f'{len(flights)} flights found from {start_city} to {city}')
                printout_flights(bot, update, flights)
            flights = api.find_connections(airport2, airport1, sunday)
            if flights:
                update.message.reply_text(f'{len(flights)} flights found from {city} to {start_city}')
                printout_flights(bot, update, flights)