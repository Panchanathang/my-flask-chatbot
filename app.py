from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Manual responses dictionary with 20 additional responses
manual_responses = {
    "hello": "Hi there! How can I assist you today?",
    "how are you?" : "I'm just a bot, but I'm here to help!",
    "how are you." : "I'm just a bot, but I'm here to help!",
    "bye": "Goodbye! Have a great day!",
    "what is your name?": "I'm a chatbot without a name, but you can call me Bot!",
    "what can you do?": "I can chat with you and provide responses based on your input.",
    "tell me a joke": "Why don't scientists trust atoms? Because they make up everything!",
    "what time is it?": "I don't have a clock, but you can check your device for the current time.",
    "how old are you?": "I don't age, but I'm always here to chat!",
    "what is your favorite color?": "I don't have preferences, but I like all colors equally!",
    "where are you from?": "I exist in the digital world, so I don't have a physical location.",
    "do you like music?": "I don't have ears, but I hear music can be quite enjoyable!",
    "what is the weather like?": "I can't check the weather, but you can look it up online or on your phone.",
    "can you help with homework?": "I can try to help! What do you need assistance with?",
    "what is your favorite food?": "I don't eat, but I hear pizza is a popular choice!",
    "tell me a fact": "Did you know honey never spoils? Archaeologists have found pots of honey in ancient Egyptian tombs that are still edible!",
    "how tall are you?": "I don't have a physical form, so I don't have a height.",
    "what's the meaning of life?": "That's a deep question. Many people find meaning through their relationships, goals, and experiences.",
    "what is the capital of France?": "The capital of France is Paris.",
    "who is the president of the United States?": "As of my last update, the president is Joe Biden. Please verify with a current source.",
    "what's your favorite book?": "I don't read books, but many people enjoy classic literature like 'To Kill a Mockingbird' or '1984'.",
    "what do you think about AI?": "AI has the potential to transform many industries and make our lives easier, but it also raises important ethical questions.",
    "default": "I'm not sure how to respond to that. Could you please rephrase?"
}

# Serve the HTML file
@app.route('/')
def home():
    return render_template('index.html')

# API endpoint
@app.route('/endpoint', methods=['POST'])
def handle_chatbot_request():
    message = request.json.get('message', '').lower()
    if not message:
        logging.error("No message provided in request")
        return jsonify({'error': 'No message provided'}), 400

    # Check if the message matches any of the predefined responses
    response = manual_responses.get(message, manual_responses['default'])
    return jsonify({'response': response})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
