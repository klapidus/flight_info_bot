import datetime
import dataclasses

@dataclasses.dataclass
class Flight:
    departure_time: datetime.time
    arrival_time: datetime.time
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
