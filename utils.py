import datetime
import dataclasses

from dataclasses_serialization.bson import BSONSerializerMixin

@dataclasses.dataclass
class Flight(BSONSerializerMixin):
    departure_airport: str
    arrival_airport: str
    departure_datetime: datetime.datetime
    arrival_datetime: datetime.datetime
    duration: int #flight duration in minutes
    airline_id: str
    flight_number: str


@dataclasses.dataclass
class FlightStatus:
    scheduled_departure: datetime.time
    actual_departure: datetime.time


def get_weekend_days():
    today = datetime.date.today()
    # assumes Friday is the 4th day, Monday being 0th
    # will return Friday, if today is Friday, that's intended
    friday = today + datetime.timedelta((4 - today.weekday()) % 7)
    saturday = friday + datetime.timedelta(1)
    sunday = friday + datetime.timedelta(2)
    return friday, saturday, sunday


# def n_latest_flights(flights):
#     print(sorted(flights, key=lambda x: x.departure_datetime,reverse=True)[:3])
#     return sorted(flights, key=lambda x: x.departure_datetime)[:-3]


# if __name__=='__main__':
#     print(BSONSerializer.serialize(InventoryItem("Apple", 0.2, 20, '14:23')))
#     print(BSONSerializer.serialize(Flight('14:23', '14:23', 10, 'LH', '1232')))
#     print(serialize(Flight('14:23', '14:23', 10, 'LH', '1232')))
