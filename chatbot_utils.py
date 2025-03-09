import re
from flight_utils import get_access_token, get_iata_code, search_flights, get_flight_status_aviation_stack
from config_chatbot import AMADEUS_CLIENT_ID, AMADEUS_CLIENT_SECRET, AVIATION_STACK_API_KEY, OPENAI_API_KEY
from langchain.memory import ConversationBufferMemory  
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain

llm = ChatOpenAI(model_name="gpt-4", temperature=0.7, openai_api_key=OPENAI_API_KEY)
memory = ConversationBufferMemory() 
conversation = ConversationChain(llm=llm, memory=memory)

def chat_with_ai(user_input):
    """Process flight-related queries using raw conversation history."""
    user_input = user_input.lower()
    conversation_history = memory.load_memory_variables({})["history"]

    # Regex patterns to capture flight details
    pattern = r"from\s+(\w+)\s+to\s+(\w+)\s+on\s+(\d{4}-\d{2}-\d{2}).*operated by\s+(\w+)"
    match = re.search(pattern, conversation_history, re.IGNORECASE)

    if match:
        dep_iata, arr_iata, flight_date, carrier_code = match.groups()
        flight_number_pattern = r"flight\s+([A-Z0-9]{2,}\d+)" 
        flight_number_match = re.search(flight_number_pattern, conversation_history, re.IGNORECASE)
        flight_number = flight_number_match.group(1) if flight_number_match else None

        token = get_access_token(AMADEUS_CLIENT_ID, AMADEUS_CLIENT_SECRET)

        if "baggage" in user_input or "luggage" in user_input:
            flights = search_flights(token, dep_iata, arr_iata, flight_date, 1)
            if flights.get("data"):
                for flight in flights["data"]:
                    for traveler in flight["travelerPricings"]:
                        for segment in traveler["fareDetailsBySegment"]:
                            baggage_info = segment["includedCheckedBags"]["quantity"]
                            return f"You are allowed {baggage_info} checked bags on your flight on {flight_date}."
            return "I couldn't find baggage information for this flight."
            
        elif "seats left" in user_input or "how many seats" in user_input:
            flights = search_flights(token, dep_iata, arr_iata, flight_date, 1)
            if flights.get("data"):
                available_seats = flights["data"][0].get("numberOfBookableSeats", "unknown")
                return f"There are {available_seats} seats left on your flight on {flight_date}."
            return "I couldn't retrieve seat availability for this flight."

        elif "layovers" in user_input or "stops" in user_input:
            flights = search_flights(token, dep_iata, arr_iata, flight_date, 1)
            if flights.get("data"):
                layovers = len(flights["data"][0]["itineraries"][0]["segments"]) - 1
                return f"Your flight on {flight_date} has {layovers} layover(s)."
            return "I couldn't retrieve layover details for this flight."

        elif "aircraft" in user_input or "plane" in user_input:
            flights = search_flights(token, dep_iata, arr_iata, flight_date, 1)
            if flights.get("data"):
                aircraft_type = flights["data"][0]["itineraries"][0]["segments"][0]["aircraft"]["code"]
                return f"Your flight on {flight_date} is operated using an {aircraft_type} aircraft."
            return "I couldn't retrieve aircraft information for this flight."

        elif "status" in user_input:
            if not flight_number:
                return "I couldn't determine your flight number. Please provide it to check status."
            try:
                flight_status = get_flight_status_aviation_stack(AVIATION_STACK_API_KEY, carrier_code, flight_number, dep_iata, arr_iata)
                if flight_status.get("data"):
                    status = flight_status["data"][0].get("flight_status", "unknown")
                    return f"Flight {flight_number} ({carrier_code}) on {flight_date}: Status is {status}."
                return "No status data available."
            except requests.HTTPError as e:
                return f"Failed to retrieve status: {str(e)}"

    return conversation.predict(input=user_input)

def save_chat_to_memory(user_message, ai_response):
    """Store raw conversation context without summarization."""
    memory.save_context({"input": user_message}, {"output": ai_response})

def get_conversation_summary():
    """Return raw conversation history instead of summary."""
    return memory.load_memory_variables({})["history"]