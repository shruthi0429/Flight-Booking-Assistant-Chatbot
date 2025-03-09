# ✈️ Flight Booking Assistant Chatbot

An AI-powered chatbot assistant for flight bookings, status checks, and travel inquiries. Integrates with Amadeus and AviationStack APIs for real-time flight data and uses GPT-4 for natural language interactions.

## Features

- **Flight Search**: Find available flights by origin, destination, and date.
- **Booking Management**: Select and book flights directly in the app.
- **Conversational AI**: Ask about baggage policies, seat availability, layovers, aircraft details, and flight status.
- **API Integrations**: 
  - Amadeus API for flight offers and IATA code lookup.
  - AviationStack API for real-time flight status.
- **Contextual Memory**: Maintains conversation history using `ConversationBufferMemory`.

---

## System Architecture

```mermaid
%%{init: {'theme': 'neutral'}}%%
graph TD
    U[User] --> SF{{Streamlit Frontend<br>(app.py)}}
    
    SF --> CU[[Chatbot Utilities<br>(chatbot_utils.py)]]
    SF --> FU[[Flight Utilities<br>(flight_utils.py)]]
    
    subgraph CU ["Chatbot Utilities Module"]
        direction TB
        MEM[[Conversation Buffer Memory]]
        CHAIN[[Conversation Chain]]
        CHAIN --> MEM[(Stores raw\nconversation history)]
        CHAIN --> GPT[[OpenAI GPT-4]]
    end
    
    FU --> AMA[(Amadeus API)]
    FU --> AVI[(AviationStack API)]
    
    CU --> CFG[[Config File<br>(config_chatbot.py)]]
    FU --> CFG
    AMA --> CFG
    AVI --> CFG
    GPT --> CFG

    style MEM fill:#e1f5fe,stroke:#039be5


## Technologies Used

- **Frontend**: Streamlit
- **Conversation Memory**: LangChain's `ConversationBufferMemory`
- **NLP Engine**: OpenAI GPT-4
- **APIs**:
  - Amadeus (Flight Offers, IATA Codes)
  - AviationStack (Flight Status)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/flight-booking-chatbot.git
   cd flight-booking-chatbot
   ```

2. **Install dependencies**:
   ```bash
   pip install streamlit langchain openai requests python-dotenv
   ```

3. **Configure API keys**:
   Create `config_chatbot.py` in the root directory:
   ```python
   # config_chatbot.py
   AMADEUS_CLIENT_ID = "your_amadeus_client_id"
   AMADEUS_CLIENT_SECRET = "your_amadeus_client_secret"
   AVIATION_STACK_API_KEY = "your_aviation_stack_key"
   OPENAI_API_KEY = "your_openai_key"
   ```

4. **Run the app**:
   ```bash
   streamlit run app.py
   ```

## Usage

### Flight Search (Sidebar)
1. Enter origin/destination cities, departure date, and passenger count.
2. Click **Search Flights**.
3. Select a flight from the list and click **Book This Flight**.

### Chat Interface (Main Panel)
- Ask questions like:
  - *"How many seats are left on my flight?"*
  - *"Check the status of flight AA123."*
  - *"What’s the baggage allowance?"*
  - *"Does this flight have layovers?"*

### Conversation Memory (Sidebar)
- View the raw interaction history stored by `ConversationBufferMemory`.

---

## Configuration

| Service             | Key Source                                   |
|---------------------|----------------------------------------------|
| Amadeus API         | [Get Credentials](https://developers.amadeus.com/) |
| AviationStack       | [Sign Up](https://aviationstack.com/)        |
| OpenAI              | [API Keys](https://platform.openai.com/api-keys) |

---


