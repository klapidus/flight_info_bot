import datetime
import requests

import settings
from utils import Flight


class LufthansaAPI:

    _LH_API_AUTH = {
                    'Accept': 'application/json',
                    'Authorization': 'XYZ'
                   }

    _LH_API_SCHEDULES_URL = 'https://api.lufthansa.com/v1/operations/schedules'
    _LH_API_FLIGHT_STATUS_URL = 'https://api.lufthansa.com/v1/operations/flightstatus'

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def _flight_by_info(self, entry):
        departure_time = entry['Flight']['Departure']['ScheduledTimeLocal']['DateTime'][-5:]
        departure_time = datetime.time(int(departure_time[:2]), int(departure_time[3:]))
        arrival_time = entry['Flight']['Arrival']['ScheduledTimeLocal']['DateTime'][-5:]
        arrival_time = datetime.time(int(arrival_time[:2]), int(arrival_time[3:]))
        duration = entry['TotalJourney']['Duration'][2:] #output: 12H59M
        duration_h, duration_m = duration.split('H')[0], duration.split('H')[1][:2]
        duration = int(duration_h)*60 + int(duration_m) #flight-time in minutes
        airline_id = entry['Flight']['MarketingCarrier']['AirlineID']
        flight_number = entry['Flight']['MarketingCarrier']['FlightNumber']
        return Flight(departure_time, arrival_time, duration, airline_id, flight_number)

    def init_token(self):
        my_data = {'client_id': self.client_id,
                   'client_secret': self.client_secret,
                   'grant_type': "client_credentials"}
        try:
            result = requests.post('https://api.lufthansa.com/v1/oauth/token', data=my_data)
            result.raise_for_status()
            self._LH_API_AUTH['Authorization'] = 'Bearer ' + result.json()['access_token']
        except (requests.RequestException, ValueError):
            return False

    def _make_request(self, url):
        res = requests.get(url, headers=self._LH_API_AUTH)
        if res.status_code == 401:
            self.init_token()
            return requests.get(url, headers=self._LH_API_AUTH)
        return res

    def find_connections(self, origin, destination, date_time, direct_flight='true'):
        schedule_url = f'{self._LH_API_SCHEDULES_URL}/{origin}/{destination}/{date_time}?directFlights={direct_flight}'
        try:
            result = self._make_request(schedule_url)
            result.raise_for_status()
            result_json = result.json()
            if 'ScheduleResource' in result_json:
                flight_schedule = result_json['ScheduleResource']['Schedule']
                if not isinstance(flight_schedule, list):
                    flight_schedule = [flight_schedule]
                return [self._flight_by_info(entry) for entry in flight_schedule]
        except (requests.RequestException, ValueError):
            return False


    def flight_status(self, full_id, date):
        status_url = f'{self._LH_API_FLIGHT_STATUS_URL}/{full_id}/{date}'
        try:
            result = self._make_request(status_url)
            result.raise_for_status()
            flight = result.json()['FlightStatusResource']['Flights']['Flight'][0]
            print('-------------')
            print('Departure scheduled:', flight['Departure']['ScheduledTimeLocal']['DateTime'][-5:])
            print('Departure actual:', flight['Departure']['ActualTimeLocal']['DateTime'][-5:])
        except (requests.RequestException, ValueError):
            return False

if __name__=='__main__':
    # get_auth_token()
    # find_connection('DME', 'FRA', '2019-12-25')
    # find_connection('DME', 'GVA', '2019-12-25')
    # find_connection('GVA', 'MUC', '2019-12-25')
    # flight_status('LH9268', '2019-12-15')
    # flight_status('LH9268', '2019-12-16')
    api = LufthansaAPI(settings.LH_CLIENT_ID, settings.LH_CLIENT_SECRET)
    api.flight_status('LH9268', '2019-12-16')