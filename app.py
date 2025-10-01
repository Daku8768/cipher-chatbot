from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import mysql.connector
import requests
import re
from datetime import datetime
import os  # <<< ADD THIS LINE
from dotenv import load_dotenv  # <<< ADD THIS LINE

load_dotenv()  # <<< ADD THIS LINE to load the .env file

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Database config
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME', 'chatbot_db'),
    'port': os.getenv('DB_PORT', 3306)
}

# Perplexity API config - NOW SAFE
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY') # <<< CHANGE THIS LINE
PERPLEXITY_URL = 'https://api.perplexity.ai/chat/completions'
MODEL_NAME = 'sonar-pro'

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"[DB] Connection error: {err}")
        return None

def preprocess_message(message: str) -> str:
    message = message.lower()
    message = re.sub(r'[^\w\s]', '', message)
    return message.strip()

def query_local_intent(message: str):
    conn = get_db_connection()
    if not conn:
        print("[DB] No connection")
        return None

    try:
        cur = conn.cursor()
        cur.execute("SELECT intent_name, pattern, response FROM intents")
        rows = cur.fetchall()
        processed = preprocess_message(message)
        print(f"[Intent Matching] Processed message: '{processed}'")
        for intent_name, pattern, response in rows:
            if not pattern:
                continue
            keywords = [k.strip().lower() for k in pattern.split('|') if k.strip()]
            print(f"[Intent Matching] Intent: '{intent_name}', Keywords: {keywords}")
            if any(keyword in processed for keyword in keywords):
                print(f"[Intent Matching] Matched intent '{intent_name}'")
                return response
        print("[Intent Matching] No matching intent found")
        return None
    except mysql.connector.Error as err:
        print(f"[DB] Query error: {err}")
        return None
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

def call_perplexity_api(message: str, reasoning: bool = False) -> str:
    if not PERPLEXITY_API_KEY:
        return "API key for Perplexity is not configured. Please check your .env file."

    headers = {
        'Authorization': f'Bearer {PERPLEXITY_API_KEY}',
        'Content-Type': 'application/json'
    }

    if reasoning:
        system_message = """You are CIPHER BOT, an intelligent AI assistant. When reasoning mode is enabled, provide detailed step-by-step analysis with clear explanations. Structure your response with:

🧠 **Step-by-Step Analysis:**

1. **Understanding**: [What the user is asking]

2. **Analysis**: [Key points to consider]

3. **Solution**: [Your detailed answer]

Keep responses comprehensive yet concise."""
    else:
        system_message = """You are CIPHER BOT, a helpful AI assistant. Provide clear, direct, and useful responses. Keep answers concise and to the point."""

    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': message}
    ]

    data = {
        'model': MODEL_NAME,
        'messages': messages,
        'max_tokens': 500 if reasoning else 300,
        'temperature': 0.7,
    }

    try:
        resp = requests.post(PERPLEXITY_URL, headers=headers, json=data, timeout=20)
        if resp.status_code == 200:
            js = resp.json()
            return js['choices'][0]['message']['content']
        else:
            print(f"[Perplexity] HTTP {resp.status_code} => {resp.text}")
            return "I'm having trouble connecting right now. Please try again in a moment."
    except requests.exceptions.RequestException as e:
        print(f"[Perplexity] Exception: {e}")
        return "I'm experiencing connectivity issues. Please try again shortly."

def save_conversation(user_id: int, message: str, response: str):
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cur = conn.cursor()
        query = "INSERT INTO conversations (user_id, message, response) VALUES (%s, %s, %s)"
        cur.execute(query, (user_id, message, response))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"[DB] Save error: {err}")
        return False
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json() or {}
        message = (data.get('message', '')).strip()
        user_id = int(data.get('user_id', 1))
        reasoning = bool(data.get('reasoning', False))

        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400

        print(f"[Chat] Message: '{message}', Reasoning: {reasoning}")

        # First try local database
        local_response = query_local_intent(message)

        if local_response and not reasoning:
            bot_response = local_response
            print("[Chat] Using local response")
        else:
            # Use Perplexity API for reasoning mode or when no local match
            bot_response = call_perplexity_api(message, reasoning)
            print("[Chat] Using Perplexity API response")

        # Save conversation to database
        save_conversation(user_id, message, bot_response)

        return jsonify({
            'response': bot_response,
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'reasoning_used': reasoning or (local_response is None)
        })
    except Exception as e:
        print(f"[Chat] Error: {e}")
        return jsonify({'error': 'Something went wrong. Please try again.'}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print("🚀 Starting CIPHER BOT Server...")
    print("📍 Server running on: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
