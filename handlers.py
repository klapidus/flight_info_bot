from flight_info import find_connection

def find_flight(bot, update, user_data):
    in_text = update.message.text
    origin, destination = in_text.split()[1][:3], in_text.split()[1][4:]
    datetime = in_text.split()[2]
    flights = find_connection(origin, destination, datetime)
    update.message.reply_text(str(len(flights))+" flights found")
    for idx, flight in enumerate(flights):
        update.message.reply_text(str(idx+1) + ': ' + flight.airline_id + flight.flight_number)
        update.message.reply_text('flight: ' + flight.departure_time + '-' + flight.arrival_time)




