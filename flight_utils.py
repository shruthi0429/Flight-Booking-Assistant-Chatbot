import os
import requests
from config_chatbot import AMADEUS_CLIENT_ID, AMADEUS_CLIENT_SECRET, AVIATION_STACK_API_KEY

def get_access_token(client_id, client_secret):
    """Get Amadeus API access token."""
    auth_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    auth_data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(auth_url, data=auth_data)
    response.raise_for_status()
    return response.json()["access_token"]

def get_iata_code(access_token, city_name):
    """Convert city name to IATA airport code."""
    url = "https://test.api.amadeus.com/v1/reference-data/locations"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"subType": "CITY,AIRPORT", "keyword": city_name}
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    data = response.json()
    return data["data"][0]["iataCode"] if data.get("data") else None

def search_flights(access_token, origin, destination, departure_date, adults, max_offers=5):
    """Search for available flights using Amadeus API."""
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": departure_date,
        "adults": adults,
        "max": max_offers
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def extract_flight_details(flight_offer):
    """Extract baggage info for all segments, including zero allowances."""
    itinerary = flight_offer["itineraries"][0]
    baggage_info = []

    for segment in itinerary["segments"]:
        segment_baggage = "Not specified"
        if "travelerPricings" in flight_offer:
            for traveler in flight_offer["travelerPricings"]:
                for seg_detail in traveler["fareDetailsBySegment"]:
                    if seg_detail["segmentId"] == segment["id"]:
                        included = seg_detail.get("includedCheckedBags", {})
                        if "quantity" in included:
                            qty = included["quantity"]
                            segment_baggage = f"{qty} checked bags"
                        elif "weight" in included:
                            wt = included["weight"]
                            unit = included.get("weightUnit", "")
                            segment_baggage = f"{wt} {unit}"
                        baggage_info.append(segment_baggage)
                        break 
    
    return {
        "carrier_code": itinerary["segments"][0]["carrierCode"],
        "flight_number": itinerary["segments"][0]["number"],
        "scheduled_dep_date": itinerary["segments"][0]["departure"]["at"].split("T")[0],
        "dep_iata": itinerary["segments"][0]["departure"]["iataCode"],
        "arr_iata": itinerary["segments"][-1]["arrival"]["iataCode"],
        "baggage_info": " + ".join(baggage_info) if baggage_info else "No baggage included"
    }
    
def get_flight_status_aviation_stack(aviation_key, carrier_code, flight_number, dep_iata, arr_iata):
    """Retrieve flight status from AviationStack API."""
    url = "http://api.aviationstack.com/v1/flights"
    params = {
        "access_key": aviation_key,
        "flight_iata": f"{carrier_code}{flight_number}",
        "dep_iata": dep_iata,
        "arr_iata": arr_iata
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()
