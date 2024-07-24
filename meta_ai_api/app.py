from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Manual responses dictionary
manual_responses = {
    "hello": "Hi there! How can I assist you today?",
    "how are you?" or "how are you." : "I'm just a bot, but I'm here to help!",
    "bye": "Goodbye! Have a great day!",
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
