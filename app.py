from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import logging
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def get_meta_ai_response(prompt):
    model_name = "facebook/blenderbot-90M-distill"
    tokenizer = BlenderbotTokenizer.from_pretrained(model_name)
    model = BlenderbotForConditionalGeneration.from_pretrained(model_name)
    
    try:
        inputs = tokenizer(prompt, return_tensors="pt", padding=True)
        reply_ids = model.generate(**inputs, max_length=512, num_return_sequences=1)
        responses = []
        for reply_id in reply_ids:
            response = tokenizer.decode(reply_id, skip_special_tokens=True)
            responses.append(response)
        return responses
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
    
    response = get_meta_ai_response(message)
    return jsonify({'response': response})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
