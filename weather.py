import requests

def get_weather(city_name, date):
    weather_url = "http://api.worldweatheronline.com/premium/v1/weather.ashx"
    params = {
        'key' : '2dafdb48aa5340bfbcb150110190512',
        'q': city_name,
        'date' : date,
        'format': 'json',
        'num_of_days': 1,
        'lang': 'en'
    }
    result = requests.get(weather_url, params=params)
    weather = result.json()
    if 'data' in weather:
        if 'current_condition' in weather['data']:
            try:
                return weather['data']['current_condition'][0]
            except(IndexError, TypeError):
                return False
    return False

def filter_good_weekend_weather(city, date):
    weather = get_weather(city, date)
    weather_temp = weather['temp_C']
    weather_desc = weather['weatherDesc'][0]['value']

    good_weather_desc = ['Sunny', 'Clear', 'Partly cloudy']
    print(f'In {city} on {date} is {weather_desc}, temperature is {weather_temp} degrees')

    return weather_desc in good_weather_desc
