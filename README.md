# AgriPrice Assistant 🌾

An AI-powered agricultural advisor that helps Indian farmers get live crop prices and farming guidance through a conversational interface.

## Features

- 🤖 **AI-Powered Conversations**: Powered by Groq's Llama 3.3 model
- 📊 **Live Crop Prices**: Real-time market data from Data.gov.in Agmarknet API
- 🌱 **Farming Advice**: Comprehensive agricultural guidance and best practices
- 💻 **Web Interface**: User-friendly web app accessible from any browser
- 🖥️ **Terminal Interface**: Command-line version for developers
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 💬 **Multi-turn Conversations**: Remembers context throughout the conversation
- 📝 **Session Logging**: Saves all conversations to a log file
- ⚡ **Fast Responses**: Instant answers for common queries, optimized API calls

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys

Create a `.env` file in the project directory:

```bash
# Copy from .env.example
cp .env.example .env

# Edit .env and add your API keys:
GROQ_API_KEY=your_groq_api_key_here
DATA_GOV_API_KEY=your_data_gov_api_key_here
```

**Get API Keys:**
- **Groq API**: Visit https://console.groq.com/ and create an account
- **Data.gov.in API**: Visit https://data.gov.in/ and register for an API key

### 3. Run the Web App (Choose your preferred interface)

#### **Streamlit App (Recommended - Modern UI)**
- **Double-click** `start_streamlit.py` in the project folder
- The browser will open automatically to http://localhost:8501

#### **Manual command**
```bash
# Streamlit version (recommended)
streamlit run streamlit_app.py
```

#### **Terminal version**
```bash
cd "c:\Users\Asus\OneDrive\Documents\AgriPrice AI Agent"
python agriprice_assistant.py
```

## Usage Examples

### Crop Price Queries
- "What's the price of wheat in Punjab?"
- "Cotton rates in Maharashtra"
- "Rice prices in West Bengal"

### Farming Advice
- "Give me farming advice"
- "How to manage pests naturally?"
- "What crops for Kharif season?"
- "Irrigation techniques"

## Project Structure

```
AgriPrice AI Agent/
├── streamlit_app.py        # Streamlit web application (recommended)
├── web_app.py              # Flask web application (alternative)
├── agriprice_assistant.py  # Terminal version
├── start_streamlit.py      # Streamlit launcher (double-click to run!)
├── templates/
│   └── index.html         # Flask web interface
├── QUICK_START.txt         # Simple instructions
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .env                  # Your API keys (create this)
├── README.md             # This file
└── session_log.txt       # Conversation logs
```

## API Integration

### Groq API
- **Model**: llama-3.3-70b-versatile
- **Purpose**: AI conversation and farming advice
- **Cost**: Very affordable compared to other LLM providers

### Data.gov.in API
- **Service**: Agmarknet agricultural market data
- **Purpose**: Live crop prices from Indian mandis
- **Coverage**: All major agricultural markets across India

## Web App Features

### Streamlit Interface (Recommended)
- **Modern Chat UI**: Clean, intuitive chat interface with message bubbles
- **Real-time Responses**: Instant AI responses with loading indicators
- **Interactive Sidebar**: Quick examples and information panel
- **Session Management**: Persistent chat history during session
- **Mobile Responsive**: Works perfectly on all devices
- **One-click Clear**: Easy chat history reset

### Flask Interface (Alternative)
- Clean, responsive design
- Real-time chat experience
- Quick action buttons for common queries
- Mobile-friendly layout

### Quick Actions Sidebar (Both versions)
- Pre-built queries for popular crops
- State-wise price lookups
- Farming advice shortcuts
- Seasonal recommendations

## Sample Conversations

### Getting Wheat Prices
```
You: What's the price of wheat in Punjab?
AgriPrice Assistant: Fetching latest market prices...
Market: Bathinda
Date: 2024-01-15
Min: ₹2200, Max: ₹2350, Modal: ₹2275 per quintal

Hello! The current market price for wheat in Punjab's Bathinda mandi shows a modal price of ₹2275 per quintal. This seems reasonable for this time of year. Do you have any specific farming questions about wheat cultivation?
```

### Farming Advice
```
You: How can I improve my tomato yield?
AgriPrice Assistant: That's a great question! Here are some tips to improve your tomato yield:

1. **Soil Preparation**: Ensure your soil has good drainage and is rich in organic matter. Tomatoes prefer slightly acidic soil (pH 6.0-6.8).

2. **Planting**: Space plants 2-3 feet apart in rows 3-4 feet apart. Plant after the last frost when soil temperature reaches 60°F.

3. **Watering**: Keep soil consistently moist but not waterlogged. Water at the base to avoid fungal diseases.

4. **Fertilization**: Use a balanced fertilizer high in potassium. Apply compost or well-rotted manure regularly.

5. **Pest Control**: Monitor for aphids, hornworms, and fungal diseases. Use organic methods when possible.

Would you like more specific advice for your region or tomato variety?
```

## Troubleshooting

### Common Issues

**"GROQ_API_KEY not configured"**
- Make sure your `.env` file exists and contains the correct API key
- Restart the application after adding the key

**"Price data not available"**
- Check your Data.gov.in API key
- Some crops/states may not have recent data
- API service might be temporarily down

**"Connection errors"**
- Check your internet connection
- API services might have rate limits
- Try again after a few minutes

### Logs
- Check `session_log.txt` for conversation history
- Streamlit app runs on `http://localhost:8501` by default
- Flask app runs on `http://localhost:5000` by default

## Development

### Running in Debug Mode
```bash
# Streamlit app (recommended)
streamlit run streamlit_app.py

# Flask web app
python web_app.py

# Terminal version
python agriprice_assistant.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

---

**Built with ❤️ for Indian farmers**