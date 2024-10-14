import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

   # Retrieve the API key from environment variables
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://aeroapi.flightaware.com/aeroapi"

def get_flights(origin, destination):
    headers = {"x-apikey": API_KEY}
    url = f"{BASE_URL}/airports/{origin}/flights/to/{destination}"
    
    # Define the date range for the query
    date_start = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    date_end = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    params = {
        "start": date_start,
        "end": date_end,
        "type": "nonstop",  # Ensure only nonstop flights are retrieved
        "max_pages": 1  # Request only the first page of data
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("flights", [])
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

def display_flights(flights, origin, destination):
    en_route_flights = []
    scheduled_flights = []

    for flight in flights:
        for segment in flight.get("segments", []):
            status = segment.get("status", "Unknown")
            actual_out = segment.get("actual_out", None)
            actual_on = segment.get("actual_on", None)

            # Determine if the flight is en route
            if actual_out and not actual_on:
                en_route_flights.append(segment)
            elif status == "Scheduled":
                scheduled_flights.append(segment)

    # Sort scheduled flights by departure time
    scheduled_flights.sort(key=lambda x: x.get("scheduled_off", ""))

    print(f"Flights from {origin} to {destination}:\n")
    print("En Route Flights:")
    for flight in en_route_flights:
        print_flight_info(flight)

    print("\nScheduled Flights:")
    for flight in scheduled_flights:
        print_flight_info(flight)

def print_flight_info(flight):
    airline = flight.get("operator", "Unknown")
    flight_number = flight.get("flight_number", "Unknown")
    status = flight.get("status", "Unknown")
    aircraft_type = flight.get("aircraft_type", "Unknown")
    departure_time_str = flight.get("scheduled_off", None)

    print(f"- {airline} {flight_number} ({aircraft_type}): {status}")

    if status == "Scheduled" and departure_time_str:
        departure_time = datetime.fromisoformat(departure_time_str.replace("Z", "+00:00"))
        time_until_departure = departure_time - datetime.now(departure_time.tzinfo)
        
        if time_until_departure > timedelta():
            hours, remainder = divmod(time_until_departure.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            print(f"  Time until departure: {hours} hours and {minutes} minutes")
        else:
            print("  Departure time has passed")

def main():
    with open("flights.txt", "r") as file:
        route = file.read().strip()
        origin, destination = route.split('-')
    
    flights = get_flights(origin, destination)
    if flights:
        display_flights(flights, origin, destination)
    else:
        print(f"No flights found for route {origin} to {destination}.")

if __name__ == "__main__":
    main()