CREATE DATABASE IF NOT EXISTS chatbot_db;
USE chatbot_db;

-- Users table
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  message TEXT NOT NULL,
  response TEXT NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Intents table for local responses
CREATE TABLE IF NOT EXISTS intents (
  id INT AUTO_INCREMENT PRIMARY KEY,
  intent_name VARCHAR(50) NOT NULL,
  pattern VARCHAR(500) NOT NULL,
  response TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default user
INSERT INTO users (username, email)
VALUES ('cipher_user', 'user@cipherbot.com')
ON DUPLICATE KEY UPDATE email=VALUES(email);

-- Insert enhanced local intents
INSERT INTO intents (intent_name, pattern, response) VALUES
('greeting', 'hello|hi|hey|good morning|good afternoon|good evening|howdy|greetings', 'Hello! Welcome to CIPHER BOT! I\'m here to help you with any questions you have. How can I assist you today?'),

('goodbye', 'bye|goodbye|see you|farewell|take care|later|exit|quit', 'Goodbye! Thank you for using CIPHER BOT. Feel free to return anytime you need assistance. Take care!'),

('help', 'help|assist|support|what can you do|how do you work|commands', 'I\'m CIPHER BOT, your AI assistant! I can:\n\n• Answer questions on various topics\n• Provide explanations and analysis\n• Help with research and information\n• Engage in conversations\n\nFor detailed responses, try enabling Reasoning mode using the 🧠 button!'),

('about', 'about|who are you|what are you|tell me about yourself|cipher bot', 'I\'m CIPHER BOT, an advanced AI assistant designed to help you with information, analysis, and conversations. I have two modes:\n\n• **Standard Mode**: Quick, direct responses\n• **Reasoning Mode**: Detailed step-by-step analysis\n\nHow can I help you today?'),

('health', 'how are you|how do you feel|are you okay|status', 'I\'m functioning perfectly and ready to assist you! All systems are operational. How are you doing today?'),

('thanks', 'thank you|thanks|appreciate it|grateful|thx', 'You\'re very welcome! I\'m glad I could help. If you have any other questions, feel free to ask!'),

('capabilities', 'what can you do|features|abilities|skills', 'I have many capabilities including:\n\n• **Information & Research**: Answer questions on various topics\n• **Analysis**: Break down complex problems\n• **Explanations**: Provide clear, detailed explanations\n• **Conversations**: Engage in natural dialogue\n• **Reasoning**: Step-by-step problem solving (when enabled)\n\nWhat would you like assistance with?'),

('weather', 'weather|temperature|forecast|rain|sunny|cloudy', 'I don\'t have access to real-time weather data in standard mode. Please enable Reasoning mode (🧠 button) for current weather information and forecasts!'),

('time', 'time|clock|date|today|now|current time', 'I don\'t have access to real-time information in standard mode. Please enable Reasoning mode (🧠 button) to get current time and date information!'),

('error_general', 'error|problem|issue|not working|broken', 'I understand you\'re experiencing an issue. For better troubleshooting and detailed analysis, please enable Reasoning mode (🧠 button) and describe your problem in detail.')

ON DUPLICATE KEY UPDATE 
  pattern = VALUES(pattern),
  response = VALUES(response);

-- Create indexes for better performance
CREATE INDEX idx_intents_pattern ON intents(pattern(100));
CREATE INDEX idx_conversations_user_timestamp ON conversations(user_id, timestamp);
CREATE INDEX idx_conversations_timestamp ON conversations(timestamp);