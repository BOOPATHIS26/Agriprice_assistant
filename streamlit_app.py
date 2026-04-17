import streamlit as st
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

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
            "limit": 100,
            "filters[state]": state_name,
            "filters[commodity]": crop_name
        }

        if not DATA_GOV_API_KEY:
            return "❌ Error: DATA_GOV_API_KEY is not set. Price lookup unavailable."

        # Make API request
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if not data.get("records"):
            return f"📊 No price data found for {crop_name} in {state_name}."

        # Process the records to get latest prices
        records = data["records"]
        records.sort(key=lambda x: x.get("arrival_date", ""), reverse=True)

        # Get the most recent record
        latest_record = records[0]

        market = latest_record.get("market", "Unknown Market")
        min_price = latest_record.get("min_price", "N/A")
        max_price = latest_record.get("max_price", "N/A")
        modal_price = latest_record.get("modal_price", "N/A")
        arrival_date = latest_record.get("arrival_date", "N/A")

        return f"""📍 **Market:** {market}
📅 **Date:** {arrival_date}
💰 **Modal Price:** ₹{modal_price}/quintal
📈 **Min Price:** ₹{min_price}/quintal
📉 **Max Price:** ₹{max_price}/quintal"""

    except requests.RequestException as e:
        return f"❌ Error fetching price data: {str(e)}"
    except Exception as e:
        return f"❌ Error processing price data: {str(e)}"

def should_get_price(user_message):
    """
    Checks if the user message contains price-related keywords.
    """
    user_lower = user_message.lower()
    return any(keyword in user_lower for keyword in PRICE_KEYWORDS)

def get_price_context(user_message):
    """
    Extracts crop and state names from user message for price lookup.
    """
    # Common crops and states
    crops = ["wheat", "rice", "maize", "cotton", "soybean", "tomato", "potato", "onion", "garlic", "chilli",
             "sugarcane", "mustard", "gram", "chickpea", "banana", "apple", "orange"]
    states = ["punjab", "haryana", "uttar pradesh", "rajasthan", "madhya pradesh", "maharashtra",
              "karnataka", "tamil nadu", "andhra pradesh", "telangana", "gujarat", "bihar",
              "west bengal", "odisha"]

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
        return "❌ Error: GROQ_API_KEY is not set. Please configure your Groq API key."

    try:
        client = Groq(api_key=GROQ_API_KEY)

        groq_messages = []
        if price_context:
            system_content = SYSTEM_PROMPT + f"\n\n📊 Current Market Price Information:\n{price_context}"
        else:
            system_content = SYSTEM_PROMPT

        groq_messages.append({"role": "system", "content": system_content})
        for msg in messages:
            role = "user" if msg["role"] == "user" else "assistant"
            groq_messages.append({"role": role, "content": msg["content"]})

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=groq_messages,
            max_tokens=1000,
            temperature=0.7
        )

        if hasattr(response.choices[0].message, 'content'):
            return response.choices[0].message.content
        return response.choices[0].message["content"].strip()

    except Exception as e:
        return f"😔 Sorry, I encountered an error: {str(e)}. Please try again."

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
        st.error(f"Error logging conversation: {e}")

def main():
    # Disable browser auto-open to prevent multiple tabs
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    
    st.set_page_config(
        page_title="🌾 AgriPrice Assistant",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🌾 AgriPrice Assistant")
    st.markdown("*Your AI-powered agricultural market advisor*")

    # Sidebar with information
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        **AgriPrice Assistant** helps farmers with:
        - 📊 Live crop prices from Indian markets
        - 🌱 Farming advice and best practices
        - 💡 Agricultural guidance in simple language
        """)

        st.header("🚀 Quick Examples")
        st.markdown("""
        Try asking:
        - "wheat price in Punjab"
        - "rice farming tips"
        - "pest control for tomatoes"
        - "soil health management"
        """)

        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.session_state.conversation_history = []
            st.rerun()

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me about crop prices or farming advice..."):
        # Add user message to display
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get timestamp for logging
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check if we need to get price information
        price_context = None
        if should_get_price(prompt):
            crop, state = get_price_context(prompt)
            if crop and state:
                with st.spinner("🔍 Fetching latest market prices..."):
                    price_context = get_crop_price(crop, state)
            else:
                price_context = "I couldn't identify the specific crop and state from your message. Please specify both crop name and state for accurate price information."

        # Add user message to conversation history
        st.session_state.conversation_history.append({"role": "user", "content": prompt})

        # Get AI response
        with st.spinner("🤔 Thinking..."):
            ai_response = call_groq_api(st.session_state.conversation_history, price_context)

        # Add AI response to conversation history
        st.session_state.conversation_history.append({"role": "assistant", "content": ai_response})

        # Display AI response
        with st.chat_message("assistant"):
            st.markdown(ai_response)

        # Add to display messages
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

        # Log the conversation
        log_conversation(timestamp, prompt, ai_response)

if __name__ == "__main__":
    # Check for required API keys
    if not GROQ_API_KEY:
        st.error("❌ GROQ_API_KEY is not configured. Please set it in your environment variables or .env file.")
        st.stop()

    if not DATA_GOV_API_KEY:
        st.warning("⚠️ DATA_GOV_API_KEY is not configured. Price lookup will be unavailable.")

    main()