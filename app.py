from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import mysql.connector
import requests
import re
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Database config
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME', 'chatbot_db'),
    'port': int(os.getenv('DB_PORT', 3306))
}

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Use v1beta endpoint to support the 'tools' field
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"





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

def call_gemini_api(message: str, reasoning: bool = False) -> str:
    if not GEMINI_API_KEY:
        return "API key for Gemini is not configured. Please check your .env file."
    
    print(f"[Gemini] Using API Key: {GEMINI_API_KEY[:4]}...{GEMINI_API_KEY[-4:]}")
    print(f"[Gemini] API URL: {GEMINI_URL[:80]}...")

    headers = {
        'Content-Type': 'application/json'
    }

    # --- NEW, CORRECTED PROMPT ---
    if reasoning:
        # This prompt instructs the AI to USE the search tool and SUMMARIZE the results.
        system_prompt = """You are CIPHER BOT, an intelligent AI assistant. 
        
        When the user asks for current events (like 'news', 'weather', or 'today'), you MUST use the integrated Google Search tool to find the most up-to-date information.
        
        Your task is to:
        1. Analyze the user's request (e.g., "news in chandigarh").
        2. Use Google Search to find relevant, recent articles.
        3. Synthesize and summarize the search results into a clear, helpful answer.
        4. Mention the sources for the information (e.g., "According to the Times of India...").
        
        Provide ONLY the final, summarized answer. Do NOT show your step-by-step analysis."""
        full_message = f"{system_prompt}\n\nUser question: {message}"
    else:
        system_prompt = "You are CIPHER BOT, a helpful AI assistant. Provide clear, direct, and useful responses. Keep answers concise and to the point."
        full_message = f"{system_prompt}\n\nUser: {message}"
    # --- END OF PROMPT CHANGE ---

    
    # This JSON structure (with top-level 'tools') is correct for the v1beta endpoint
    data = {
        "contents": [
            {
                "parts": [
                    {"text": full_message}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 500 if reasoning else 300,
        },
        "tools": [
            {
                "googleSearch": {}
            }
        ]
    }

    try:
        # Increased timeout for search
        resp = requests.post(GEMINI_URL, headers=headers, json=data, timeout=30) 
        if resp.status_code == 200:
            js = resp.json()
            if 'candidates' in js and len(js['candidates']) > 0:
                text = js['candidates'][0]['content']['parts'][0]['text']
                
                return text
            else:
                print(f"[Gemini] Unexpected response format: {js}")
                return "I received an unexpected response. Please try again."
        else:
            print(f"[Gemini] HTTP {resp.status_code} => {resp.text}")
            # Updated error message based on common issues
            if resp.status_code == 404:
                return "Error: The AI model was not found. Please verify the model name and API version."
            elif resp.status_code == 400:
                 # This handles API errors including bad JSON structure or key issues
                 return "Error: Bad request. Please check your API key and prompt structure."
            return "I'm having trouble connecting right now. Please try again in a moment."
    except requests.exceptions.RequestException as e:
        print(f"[Gemini] Exception: {e}")
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
            # Use Gemini API for reasoning mode or when no local match (now with search)
            bot_response = call_gemini_api(message, reasoning)
            print("[Chat] Using Gemini API response")

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
    print("🌐 Server running on: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)