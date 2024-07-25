from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import logging
import requests
from datetime import datetime
from timezonefinder import TimezoneFinder
import pytz

from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize the Meta AI model and tokenizer
model_name = "facebook/blenderbot-400M-distill"  # Example model name
tokenizer = BlenderbotTokenizer.from_pretrained(model_name)
model = BlenderbotForConditionalGeneration.from_pretrained(model_name)

def get_time_in_place(location):
    try:
        geocode_url = 'https://nominatim.openstreetmap.org/search'
        params = {'q': location, 'format': 'json'}
        headers = {
            'User-Agent': 'YourAppName/1.0 (your-email@example.com)'
        }
        response = requests.get(geocode_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()[0]
        lat, lon = float(data['lat']), float(data['lon'])
        timezone_str = TimezoneFinder().timezone_at(lng=lon, lat=lat)
        if timezone_str:
            tz = pytz.timezone(timezone_str)
            local_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            return f"The current time in {location} is {local_time} ({timezone_str})."
        else:
            return "Sorry, I couldn't find the timezone for the specified location."
    except requests.RequestException as e:
        logging.error(f"Error getting time in place: {e}")
        return "Sorry, I couldn't retrieve the time information."


def get_weather(location):
    try:
        api_key = '719bd80d49c84259bedd8616a7179ca7' 
        # Replace with your OpenWeatherMap API key
        base_url = 'https://api.weatherbit.io/v2.0/current'
        params = {
        'city': location,
        'key': api_key,
        }
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        if 'data' in data and data['data']:
            weather_data = data['data'][0]
            weather_description = weather_data['weather']['description']
            temperature = weather_data['temp']
            return f"The current weather in {location} is {weather_description} with a temperature of {temperature}°C."
        else:
            return "I'm sorry, I couldn't retrieve the weather information for the specified location."
    except requests.RequestException as e:
        logging.error(f"Error getting weather: {e}")
        return "I'm sorry, I couldn't retrieve the weather information."


def get_meta_ai_response(prompt):
    try:
        inputs = tokenizer(prompt, return_tensors="pt")
        reply_ids = model.generate(**inputs)
        response = tokenizer.decode(reply_ids[0], skip_special_tokens=True)
        return response
    except Exception as e:
        logging.error(f"Error getting response from Meta AI model: {e}")
        return "I'm sorry, I couldn't process your request at the moment."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/endpoint', methods=['POST'])
def handle_chatbot_request():
    message = request.json.get('message', '').lower()
    if not message:
        logging.error("No message provided in request")
        return jsonify({'error': 'No message provided'}), 400
    
    if "current time in" in message:
        location = message.replace("current time in ", "").strip()
        response = get_time_in_place(location)

    elif "current weather in" in message or "weather in" in message or "temperature in" in message:
        import re
        match = re.search(r'in (.*)', message)
        if match:
            location = match.group(1)
            response = get_weather(location)
        else:
            response = "Sorry, I couldn't understand the location."
    else:
    
        response = get_meta_ai_response(message)
    return jsonify({'response': response})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
