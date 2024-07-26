from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import logging
from datetime import datetime
import pytz
import requests
from timezonefinder import TimezoneFinder
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Manual responses dictionary with keywords
manual_responses = {
    "greetings": ["hello", "hi", "hey"],
    "farewells": ["bye", "goodbye"],
    "jokes": ["joke", "tell me a joke"],
    "color": ["favorite color", "color"],
    "origin": ["where are you from"],
    "music": ["do you like music"],
    "homework": ["homework", "help with homework"],
    "food": ["favorite food", "food"],
    "facts": ["fact", "tell me a fact"],
    "height": ["how tall are you"],
    "philosophy": ["meaning of life"],
    "capital": ["capital of France"],
    "book": ["favorite book"],
    "ai": ["what do you think about AI"],

}

# Manual responses mapped to keywords
responses = {
    "greetings": "Hello! It's nice to meet you. Is there something I can help you with or would you like to chat? I'm here to assist you with any questions or tasks you may have.",
    "farewells": "Goodbye! Have a great day!",
    "jokes": "Why don't scientists trust atoms? Because they make up everything!",
    "color": "I don't have preferences, but I like all colors equally!",
    "origin": "I exist in the digital world, so I don't have a physical location.",
    "music": "I don't have ears, but I hear music can be quite enjoyable!",
    "homework": "I can try to help! What do you need assistance with?",
    "food": "I don't eat, but I hear pizza is a popular choice!",
    "facts": "Did you know honey never spoils? Archaeologists have found pots of honey in ancient Egyptian tombs that are still edible!",
    "height": "I don't have a physical form, so I don't have a height.",
    "philosophy": "That's a deep question. Many people find meaning through their relationships, goals, and experiences.",
    "capital": "The capital of France is Paris.",
    "book": "I don't read books, but many people enjoy classic literature like 'To Kill a Mockingbird' or '1984'.",
    "ai": "AI has the potential to transform many industries and make our lives easier, but it also raises important ethical questions."
}


def get_meta_ai_response(prompt):
model_name = "facebook/blenderbot-90M-distill"
tokenizer = BlenderbotTokenizer.from_pretrained(model_name)
model = BlenderbotForConditionalGeneration.from_pretrained(model_name)

try:
inputs = tokenizer(prompt, return_tensors="pt")
reply_ids = model.generate(**inputs)
response = tokenizer.decode(reply_ids[0], skip_special_tokens=True)
return response
except Exception as e:
logging.error(f"Error getting response from Meta AI model: {e}")
return "I'm sorry, I couldn't process your request at the moment."

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


def find_response(message):
    message = message.lower()
    for category, keywords in manual_responses.items():
        if any(keyword in message for keyword in keywords):
            return responses[category]
    return 'Sorry, I don\'t understand that request.'


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
    elif "current weather in" in message or "weather in" in message:
        import re
        match = re.search(r'in (.*)', message)
        if match:
            location = match.group(1)
            response = get_weather(location)
        else:
            response = "Sorry, I couldn't understand the location."
    elif "day" in message:
        current_day = datetime.now().strftime("%A")
        response = f"Today is {current_day}."
    elif "place" in message:
        response = "I don't have any specific place."
    elif "president" in message and "USA" in message: 
        response = "The President of the United States is Joe Biden."
    elif "president" in message and "russia" in message.lower(): 
        response = "The President of Russia is Vladimir Putin."
    elif "who are you" in message or "your name" in message or "what can you do" in message: 
        response = "I'm an AI. Think of me like an assistant who's here to help you learn, plan, and create. How can I assist you?"
    elif "how old are you" in message or "your age" in message: 
        response = "I don't age, but I'm always here to chat! I was released to the public in 2023."
    elif "do you like math" in message or "math" in message: 
        response = "Math is a powerful tool in many fields. Do you have a specific question?"
    elif "culture" in message or "different cultures" in message: 
        response = "Cultures are diverse and rich in traditions. What are you curious about?"
    elif "languages" in message or "you speak" in message: 
        response = (
            "I can understand and respond in multiple languages! I'm proficient in many languages, including but not limited to:<br>"
            "English <br>"
            "Spanish<br>"
            "French<br>"
            "German<br>"
            "Italian<br>"
            "Portuguese<br>"
            "Dutch<br>"
            "Russian<br>"
            "Chinese (Simplified and Traditional)<br>"
            "Japanese<br>"
            "Korean<br>"
            "Arabic<br>"
            "Hebrew<br>"
            "Hindi<br>"
        )
    else:
        response = get_meta_ai_response(message)

    # Ensure response is always returned
    return jsonify({'response': response})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
