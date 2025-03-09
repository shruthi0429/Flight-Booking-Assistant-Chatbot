import streamlit as st
from flight_utils import get_access_token, get_iata_code, search_flights, extract_flight_details, get_flight_status_aviation_stack
from chatbot_utils import chat_with_ai, save_chat_to_memory, get_conversation_summary
from config_chatbot import AMADEUS_CLIENT_ID, AMADEUS_CLIENT_SECRET, AVIATION_STACK_API_KEY

if "messages" not in st.session_state:
    st.session_state.messages = []
if "offers" not in st.session_state:
    st.session_state.offers = None
if "selected_offer" not in st.session_state:
    st.session_state.selected_offer = None
if "dep_date_str" not in st.session_state:
    st.session_state.dep_date_str = None

st.title("✈️ Flight Booking Assistant")
st.sidebar.header("Flight Search")

# Flight Search Inputs
origin_city = st.sidebar.text_input("Enter Origin City")
destination_city = st.sidebar.text_input("Enter Destination City")
departure_date = st.sidebar.date_input("Select Departure Date")
adults = st.sidebar.number_input("Number of Adults", min_value=1, value=1, step=1)

# Search Flights Action
if st.sidebar.button("Search Flights"):
    token = get_access_token(AMADEUS_CLIENT_ID, AMADEUS_CLIENT_SECRET)
    origin_iata = get_iata_code(token, origin_city)
    destination_iata = get_iata_code(token, destination_city)

    if not origin_iata or not destination_iata:
        st.error("Unable to retrieve IATA codes for the provided cities.")
    else:
        st.session_state.dep_date_str = departure_date.strftime("%Y-%m-%d")  
        offers = search_flights(token, origin_iata, destination_iata, st.session_state.dep_date_str, adults)
        if not offers.get("data"):
            st.error("No flight offers found for the given route and date.")
        else:
            st.session_state.offers = offers  

# Display Flight Options
if st.session_state.offers and st.session_state.offers.get("data"):
    st.write("### Available Flights:")
    flight_options = []
    for idx, offer in enumerate(st.session_state.offers["data"], start=1):
        segment = offer["itineraries"][0]["segments"][0]
        flight_num = f"{segment['carrierCode']}{segment['number']}"
        price = offer.get("price", {}).get("total", "N/A")
        option_text = f"Option {idx}: Flight {flight_num} - {price} EUR"
        flight_options.append(option_text)
    
    selected_option = st.radio("Select a Flight", flight_options)
    
    if st.button("Book This Flight"):
        st.session_state.selected_offer = st.session_state.offers["data"][flight_options.index(selected_option)]
        flight_details = extract_flight_details(st.session_state.selected_offer)
        memory_text = (f"User selected flight {flight_details['flight_number']} from {flight_details['dep_iata']} "
                       f"to {flight_details['arr_iata']} on {st.session_state.dep_date_str}. Flight is operated by {flight_details['carrier_code']}.")
        save_chat_to_memory(memory_text, f"Great choice! Your flight {flight_details['flight_number']} is booked for {st.session_state.dep_date_str}.")
        st.success(f"Flight {flight_details['flight_number']} from {flight_details['dep_iata']} to {flight_details['arr_iata']} booked! ✅")

# Flight Status Check 
if st.session_state.selected_offer and st.button("Check Flight Status"):
    flight_details = extract_flight_details(st.session_state.selected_offer)
    status_data = get_flight_status_aviation_stack(
        AVIATION_STACK_API_KEY,
        flight_details["carrier_code"],
        flight_details["flight_number"],
        flight_details["dep_iata"],
        flight_details["arr_iata"]
    )
    st.subheader("Flight Status Information")
    st.json(status_data)

# Chat Interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle new message
user_query = st.chat_input("Type your message:")
if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    response = chat_with_ai(user_query)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
    
# Conversation Memory
st.sidebar.subheader("Conversation Memory")
st.sidebar.text_area("Memory", get_conversation_summary(), height=200)