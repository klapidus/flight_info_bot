from pymongo import MongoClient
from dataclasses_serialization.bson import BSONSerializer

import settings
import utils

#add a non-available (from API) flight to a separate collection
def insert_na_flight_to_db(db, departure, destination, dep_date):
    db.naflights2.insert_one({'departure_airport': departure,
                             'arrival_airport': destination,
                             'departure_datetime': dep_date.strftime('%Y-%m-%d')})

def is_na_flight_in_db(db, departure, destination, dep_date):
    flight = db.naflights2.find_one({'departure_airport': departure,
                                    'arrival_airport': destination,
                                    'departure_datetime': dep_date.strftime('%Y-%m-%d')}
                                   )
    if flight:
        return True
    return False


def insert_flights_to_db(db, flights):
    db.flights2.insert_many([flight.as_bson() for flight in flights])


def find_flights_from_db(db, departure, destination, dep_date):

    entries = db.flights2.find({'departure_airport': departure, 'arrival_airport': destination}, {'_id': False})
    #todo improve query by date
    #datetime object is saved in the db
    #need to project on date only
    #selection by hand for now:
    flights = []
    for entry in entries:
        flight = BSONSerializer.deserialize(utils.Flight, entry)
        if flight.departure_datetime.date() == dep_date:
            flights.append(flight)
    return flights


db = MongoClient(settings.MONGO_LINK)[settings.MONGO_DB]
