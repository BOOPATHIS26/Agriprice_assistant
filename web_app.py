from flask import Flask, render_template, request, jsonify
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

# Initialize Flask app
app = Flask(__name__)

# System prompt for the AI agent
SYSTEM_PROMPT = """
You are AgriPrice Assistant, an expert Indian agricultural market advisor. You help farmers get live crop prices and provide farming advice in simple, helpful language. Always respond in English only. Provide clear, practical, and supportive agricultural guidance.
"""

# Price-related keywords to trigger price lookup
PRICE_KEYWORDS = ["price", "rate", "cost", "mandi", "market", "today", "current", "selling", "buying"]

# Conversation history storage (in production, use a database)
conversation_history = []

# Simple response cache for common queries
response_cache = {
    "hello": "Hello! I'm your AgriPrice Assistant. I can help you with crop prices and farming advice. What would you like to know?",
    "hi": "Hi there! I'm here to help with agricultural information. Ask me about crop prices or farming tips!",
    "help": "I can help you with:\n• Live crop prices (wheat, rice, cotton, etc.)\n• Farming advice and best practices\n• Seasonal recommendations\n• Pest control tips\n\nTry asking: 'wheat price in Punjab' or 'farming advice'",
    "farming advice": "Here are some key farming tips:\n\n1. **Soil Health**: Test your soil pH and nutrients regularly\n2. **Water Management**: Use drip irrigation to save water\n3. **Crop Rotation**: Rotate crops to maintain soil fertility\n4. **Pest Control**: Use neem-based organic pesticides\n5. **Record Keeping**: Maintain a farm diary\n\nWhat specific crop or issue interests you?",
    "give me farming advice": "Here are essential farming tips:\n\n• **Soil Testing**: Check pH levels (ideal: 6.0-7.0)\n• **Irrigation**: Water early morning or evening\n• **Fertilizers**: Use balanced NPK fertilizers\n• **Pest Management**: Monitor crops regularly\n• **Harvesting**: Harvest at optimal maturity\n\nAsk me about specific crops for detailed advice!",
    "how to improve crop yield": "To improve crop yield:\n\n1. **Soil Preparation**: Deep plow and add organic matter\n2. **Quality Seeds**: Use certified, high-yielding varieties\n3. **Proper Spacing**: Follow recommended plant spacing\n4. **Irrigation**: Provide adequate water at right times\n5. **Fertilization**: Apply nutrients based on soil tests\n6. **Pest Control**: Regular monitoring and timely action\n7. **Weed Management**: Keep fields weed-free\n\nWhich crop are you growing?",
    "pest control": "Natural pest control methods:\n\n• **Neem Oil**: Effective against many pests\n• **Garlic/Chili Spray**: Repels insects\n• **Companion Planting**: Plant pest-repelling crops together\n• **Biological Control**: Introduce beneficial insects\n• **Crop Rotation**: Prevents pest buildup\n• **Physical Barriers**: Use nets or row covers\n\nAlways identify the pest first for best control method!",
    "irrigation tips": "Smart irrigation practices:\n\n• **Drip Irrigation**: Most water-efficient method\n• **Sprinkler Systems**: Good for large areas\n• **Timing**: Water early morning or evening\n• **Soil Moisture**: Check soil before watering\n• **Mulching**: Reduces evaporation\n• **Rainwater Harvesting**: Collect and store rainwater\n\nChoose method based on your crop and water availability!",
    "soil health": "Maintain healthy soil:\n\n• **pH Testing**: Keep between 6.0-7.0\n• **Organic Matter**: Add compost regularly\n• **Nutrient Balance**: Test and replenish NPK\n• **Microorganisms**: Use beneficial bacteria/fungi\n• **Avoid Over-tilling**: Preserve soil structure\n• **Cover Crops**: Prevent erosion\n\nHealthy soil = Better yields!",
    "wheat farming": "Wheat farming tips:\n\n• **Sowing Time**: October-November (Rabi season)\n• **Seed Rate**: 100-125 kg per hectare\n• **Fertilizer**: 120-150 kg NPK per hectare\n• **Irrigation**: 4-5 irrigations needed\n• **Pests**: Watch for aphids and termites\n• **Harvest**: March-April when grains are hard\n\nWheat needs cool weather for best growth!",
    "rice farming": "Rice cultivation guide:\n\n• **Land Preparation**: Puddle the field well\n• **Seed Rate**: 20-25 kg per hectare\n• **Water Management**: Maintain 5-10 cm water level\n• **Fertilizer**: Apply in splits (basal + tillering + panicle)\n• **Weed Control**: Early weed removal crucial\n• **Pest Control**: Monitor for stem borers, leaf folders\n\nRice needs plenty of water but good drainage too!",
}

def call_groq_api(user_message, conversation_history):
    """Call Groq API for AI responses"""
    try:
        client = Groq(api_key=GROQ_API_KEY)

        # Prepare messages with system prompt and history
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add conversation history (last 10 messages to avoid token limits)
        for msg in conversation_history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            max_tokens=800,  # Reduced from 1000 for faster responses
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}. Please try again."

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

        # Make API request with shorter timeout
        response = requests.get(url, params=params, timeout=8)  # Reduced from 10 to 8 seconds
        response.raise_for_status()

        data = response.json()

        if not data.get("records"):
            return f"No recent price data found for {crop_name} in {state_name}. Try a different state or check back later."

        # Process and format the price data (limit to 3 records for speed)
        records = data["records"][:3]  # Reduced from 5 to 3 for faster response
        prices = []

        for record in records:
            market = record.get("market", "Unknown Market")
            min_price = record.get("min_price", "N/A")
            max_price = record.get("max_price", "N/A")
            modal_price = record.get("modal_price", "N/A")
            date = record.get("arrival_date", "N/A")

            prices.append(f"📍 {market}: ₹{modal_price}/quintal (Min: ₹{min_price}, Max: ₹{max_price})")

        return "\n".join(prices)

    except requests.exceptions.RequestException as e:
        return f"Error fetching price data: {str(e)}. Please try again later."
    except Exception as e:
        return f"Error processing price data: {str(e)}"

def should_get_price(message):
    """Check if the message contains price-related keywords"""
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in PRICE_KEYWORDS)

def extract_crop_and_state(message):
    """Extract crop name and state from user message"""
    # Simple extraction - in production, use NLP for better accuracy
    message_lower = message.lower()

    # Common crops
    crops = ["wheat", "rice", "cotton", "sugarcane", "maize", "corn", "soybean", "mustard", "gram", "chickpea", "potato", "onion", "tomato", "banana", "apple", "orange"]

    # Common states
    states = ["punjab", "haryana", "rajasthan", "uttar pradesh", "madhya pradesh", "maharashtra", "karnataka", "tamil nadu", "andhra pradesh", "telangana", "gujarat", "bihar", "west bengal", "odisha"]

    crop_found = None
    state_found = None

    for crop in crops:
        if crop in message_lower:
            crop_found = crop.title()
            break

    for state in states:
        if state in message_lower:
            state_found = state.title()
            break

    return crop_found, state_found

@app.route('/')
def home():
    """Render the main chat interface"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'error': 'Empty message'}), 400

        # Add user message to history
        conversation_history.append({"role": "user", "content": user_message})

        # Check cache first for instant responses
        user_lower = user_message.lower().strip()
        if user_lower in response_cache:
            ai_response = response_cache[user_lower]
            conversation_history.append({"role": "assistant", "content": ai_response})
            log_conversation(user_message, ai_response)
            return jsonify({
                'response': ai_response,
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'cached': True
            })

        # Check if price lookup is needed
        if should_get_price(user_message):
            crop, state = extract_crop_and_state(user_message)
            if crop and state:
                price_info = get_crop_price(crop, state)
                # Create a combined message for the AI
                ai_input = f"User asked: {user_message}\n\nPrice information: {price_info}\n\nPlease provide helpful context and advice based on this price data."
            else:
                ai_input = user_message + "\n\nPlease help identify the crop and state for price lookup, or provide general farming advice."
        else:
            ai_input = user_message

        # Get AI response
        ai_response = call_groq_api(ai_input, conversation_history)

        # Add AI response to history
        conversation_history.append({"role": "assistant", "content": ai_response})

        # Log conversation
        log_conversation(user_message, ai_response)

        return jsonify({
            'response': ai_response,
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'cached': False
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear', methods=['POST'])
def clear_history():
    """Clear conversation history"""
    global conversation_history
    conversation_history = []
    return jsonify({'status': 'cleared'})

def log_conversation(user_message, ai_response):
    """Log conversations to file"""
    try:
        with open("session_log.txt", "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"\n[{timestamp}]\nUser: {user_message}\nAssistant: {ai_response}\n{'-'*50}\n")
    except Exception as e:
        print(f"Logging error: {e}")

if __name__ == '__main__':
    if not GROQ_API_KEY:
        print("Error: GROQ_API_KEY is not configured. Set it in your environment or in a .env file.")
        exit(1)

    print("Starting AgriPrice Assistant Web App...")
    print("Open your browser and go to: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)