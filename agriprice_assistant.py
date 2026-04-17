import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from a .env file if present
load_dotenv()

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")      # Set your Groq API key as environment variable
DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY")    # Set your Data.gov.in API key as environment variable

GROQ_MODEL = "llama-3.3-70b-versatile"  # Cost-efficient Groq model

# System prompt for the AI agent
SYSTEM_PROMPT = """
You are AgriPrice Assistant, an expert Indian agricultural market advisor. You help farmers get live crop prices and provide farming advice in simple, helpful language. Always respond in English only. Provide clear, practical, and supportive agricultural guidance.
"""

# Price-related keywords to trigger price lookup
PRICE_KEYWORDS = ["price", "rate", "cost", "mandi", "market", "today", "current", "selling", "buying"]

def get_crop_price(crop_name, state_name):
    """
    Fetches live crop prices from Data.gov.in Agmarknet API.
    Returns min/max/modal price and market name for the specified crop and state.
    """
    try:
        # API endpoint and parameters
        url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
        params = {
            "api-key": DATA_GOV_API_KEY,
            "format": "json",
            "limit": 100,  # Get more records to filter
            "filters[state]": state_name,
            "filters[commodity]": crop_name
        }

        if not DATA_GOV_API_KEY:
            return "Error: DATA_GOV_API_KEY is not set. Price lookup unavailable."

        # Make API request
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if not data.get("records"):
            return f"No price data found for {crop_name} in {state_name}."

        # Process the records to get latest prices
        records = data["records"]
        # Sort by arrival_date descending to get latest prices
        records.sort(key=lambda x: x.get("arrival_date", ""), reverse=True)

        # Get the most recent record
        latest_record = records[0]

        market = latest_record.get("market", "Unknown Market")
        min_price = latest_record.get("min_price", "N/A")
        max_price = latest_record.get("max_price", "N/A")
        modal_price = latest_record.get("modal_price", "N/A")

        return f"Market: {market}\nMin Price: ₹{min_price}/quintal\nMax Price: ₹{max_price}/quintal\nModal Price: ₹{modal_price}/quintal"

    except requests.RequestException as e:
        return f"Error fetching price data: {str(e)}"
    except Exception as e:
        return f"Error processing price data: {str(e)}"

def should_get_price(user_message):
    """
    Checks if the user message contains price-related keywords.
    """
    user_lower = user_message.lower()
    return any(keyword in user_lower for keyword in PRICE_KEYWORDS)

def get_price_context(user_message):
    """
    Extracts crop and state names from user message for price lookup.
    This is a simple implementation - in production, you might use NLP.
    """
    # Simple extraction - look for common crops and states
    crops = ["wheat", "rice", "maize", "cotton", "soybean", "tomato", "potato", "onion", "garlic", "chilli"]
    states = ["punjab", "haryana", "uttar pradesh", "rajasthan", "madhya pradesh", "maharashtra", "karnataka", "tamil nadu", "andhra pradesh", "telangana"]

    user_lower = user_message.lower()
    crop_found = None
    state_found = None

    for crop in crops:
        if crop in user_lower:
            crop_found = crop.capitalize()
            break

    for state in states:
        if state in user_lower:
            state_found = state.title()
            break

    return crop_found, state_found

def call_groq_api(messages, price_context=None):
    """
    Calls the Groq API with conversation history and optional price context.
    """
    if not GROQ_API_KEY:
        return "Error: GROQ_API_KEY is not set. Please configure your Groq API key."

    try:
        client = Groq(api_key=GROQ_API_KEY)

        groq_messages = []
        if price_context:
            system_content = SYSTEM_PROMPT + f"\n\nCurrent Market Price Information:\n{price_context}"
        else:
            system_content = SYSTEM_PROMPT

        groq_messages.append({"role": "system", "content": system_content})
        for msg in messages:
            role = "user" if msg["role"] == "user" else "assistant"
            groq_messages.append({"role": role, "content": msg["content"]})

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=groq_messages,
            max_completion_tokens=1000,
            temperature=0.7
        )

        if hasattr(response.choices[0].message, 'content'):
            return response.choices[0].message.content
        return response.choices[0].message["content"].strip()

    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}. Please try again."


def call_llm_api(messages, price_context=None):
    """
    Calls the Groq API (only provider supported).
    """
    return call_groq_api(messages, price_context)


def log_conversation(timestamp, user_input, agent_response):
    """
    Logs the conversation turn to session_log.txt
    """
    try:
        with open("session_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}]\n")
            f.write(f"User: {user_input}\n")
            f.write(f"Assistant: {agent_response}\n")
            f.write("-" * 50 + "\n")
    except Exception as e:
        print(f"Error logging conversation: {e}")

def main():
    """
    Main chat loop for the AgriPrice Assistant
    """
    print("Welcome to AgriPrice Assistant!")
    print("I'm here to help you with crop prices and farming advice.")
    print("Type 'exit' to quit.\n")

    # Initialize conversation history
    conversation_history = []

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            if user_input.lower() == "exit":
                print("Thank you for using AgriPrice Assistant. Goodbye!")
                break

            if not user_input:
                continue

            # Get timestamp for logging
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Check if we need to get price information
            price_context = None
            if should_get_price(user_input):
                crop, state = get_price_context(user_input)
                if crop and state:
                    print("Fetching latest market prices...")
                    price_context = get_crop_price(crop, state)
                else:
                    price_context = "I couldn't identify the specific crop and state from your message. Please specify both crop name and state for accurate price information."

            # Add user message to history
            conversation_history.append({"role": "user", "content": user_input})

            # Get AI response
            ai_response = call_llm_api(conversation_history, price_context)

            # Add AI response to history
            conversation_history.append({"role": "assistant", "content": ai_response})

            # Display response
            print(f"AgriPrice Assistant: {ai_response}\n")

            # Log the conversation
            log_conversation(timestamp, user_input, ai_response)

        except KeyboardInterrupt:
            print("\nThank you for using AgriPrice Assistant. Goodbye!")
            break
        except EOFError:
            print("\nInput closed. Exiting AgriPrice Assistant. Goodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

if __name__ == "__main__":
    if not GROQ_API_KEY:
        print("Error: GROQ_API_KEY is not configured. Set it in your environment or in a .env file.")
        exit(1)
    if not DATA_GOV_API_KEY:
        print("Warning: DATA_GOV_API_KEY is not configured. Price lookup will be unavailable.")
    main()