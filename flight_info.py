import requests

import settings
from utils import Flight

def get_auth_token():
    my_data = {'client_id': settings.LH_CLIENT_ID,
               'client_secret': settings.LH_CLIENT_SECRET,
               'grant_type': "client_credentials"}
    try:
        result = requests.post('https://api.lufthansa.com/v1/oauth/token', data=my_data)
        result.raise_for_status()
        settings.LH_API_AUTH['Authorization'] = 'Bearer ' + result.json()['access_token']
    except (requests.RequestException, ValueError):
        return False

def find_connection(origin, destination, datetime, direct_flight='true'):
    schedule_url = settings.LH_API_SCHEDULES_URL +\
                   '{}/{}/{}?directFlights={}'.format(origin, destination, datetime, direct_flight)
    try:
        result = requests.get(schedule_url, headers=settings.LH_API_AUTH)
        result.raise_for_status()

        if 'ScheduleResource' in result.json():
            flight_schedule = result.json()['ScheduleResource']['Schedule']
            if not isinstance(flight_schedule, list):
                flight_schedule = [flight_schedule]
            flights = []
            for idx, entry in enumerate(flight_schedule):
                departure_time = entry['Flight']['Departure']['ScheduledTimeLocal']['DateTime'][-5:]
                arrival_time = entry['Flight']['Arrival']['ScheduledTimeLocal']['DateTime'][-5:]
                duration = entry['TotalJourney']['Duration'][2:]
                airline_id = entry['Flight']['MarketingCarrier']['AirlineID']
                flight_number = entry['Flight']['MarketingCarrier']['FlightNumber']
                flights.append(Flight(departure_time, arrival_time, duration, airline_id, flight_number))
            return flights
    except (requests.RequestException, ValueError):
        return False


def flight_status(full_id, date):
    status_url = settings.LH_API_FLIGHT_STATUS_URL + \
                 '{}/{}'.format(full_id, date)
    try:
        result = requests.get(status_url, headers=settings.LH_API_AUTH)
        result.raise_for_status()
        flight = result.json()['FlightStatusResource']['Flights']['Flight'][0]
        # print('-------------')
        print('Departure scheduled:', flight['Departure']['ScheduledTimeLocal']['DateTime'][-5:])
        print('Departure actual:', flight['Departure']['ActualTimeLocal']['DateTime'][-5:])
    except (requests.RequestException, ValueError):
        return False

if __name__=='__main__':
    get_auth_token()
    find_connection('DME', 'FRA', '2019-12-25')
    # find_connection('DME', 'GVA', '2019-12-25')
    # find_connection('GVA', 'MUC', '2019-12-25')
    flight_status('LH9268', '2019-12-15')
    # flight_status('LH9268', '2019-12-16')
    # flight_status('LH9268', '2019-12-17')