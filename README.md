🤖 CIPHER BOT - AI Chatbot Project
CIPHER BOT is an intelligent chatbot built with Python and Flask. It uses a local MySQL database for quick, predefined responses and integrates with the Perplexity API for advanced, real-time query processing and step-by-step reasoning.

✨ Features
Dual-Mode Operation:

Standard Mode: Provides instant answers to common questions (like greetings, goodbyes, and help) by querying a local MySQL database for maximum speed.

Reasoning Mode (🧠): Leverages the powerful sonar-pro model via the Perplexity API to deliver detailed, step-by-step analysis for complex questions.

Conversation Logging: All interactions are saved to the database, linking messages and responses to a user.

Robust Backend: Built with Flask, providing a stable and scalable web server.

Database Driven: Uses MySQL to store user data, conversation history, and predefined "intents" for fast lookups.

🛠️ Tech Stack
Backend: Python, Flask

Database: MySQL

API: Perplexity AI

Libraries: Flask-CORS, mysql-connector-python, requests, python-dotenv

🚀 How to Run This Project Locally
Follow these instructions to get a copy of the project up and running on your local machine.

Prerequisites
Python 3.8+

Git

MySQL Server: Ensure you have a running MySQL instance.

1. Clone the Repository
First, clone this repository to your local machine.

git clone [https://github.com/your-username/cipher-chatbot.git](https://github.com/your-username/cipher-chatbot.git)
cd cipher-chatbot

Replace your-username/cipher-chatbot with your repository's URL.

2. Set Up a Virtual Environment
It is highly recommended to use a virtual environment to manage project dependencies.

# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

3. Install Dependencies
Install all the required Python libraries using the requirements.txt file.

pip install -r requirements.txt

4. Configure the Database
You need to set up the database and tables using the provided SQL script.

Log in to your MySQL server.

Run the database_setup.sql script. This will create the chatbot_db database, the necessary tables (users, conversations, intents), and insert the default intents.

You can do this via a tool like MySQL Workbench or from the command line:

mysql -u root -p < database_setup.sql

You will be prompted to enter your MySQL root password.

5. Create the Environment File (.env)
This project uses a .env file to manage sensitive information like database credentials and API keys.

Create a new file named .env in the root of the project folder.

Copy the content below into the file and replace the placeholder values with your actual credentials.

# Database Configuration
DB_HOST=localhost
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=chatbot_db
DB_PORT=3306

# Perplexity API Configuration
PERPLEXITY_API_KEY=your_perplexity_api_key_here

# Flask Configuration
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

6. Run the Application
You are now ready to start the server!

python app.py

The server will start, and you can access the chatbot by navigating to http://localhost:5000 in your web browser.