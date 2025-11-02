# 🤖 CIPHER BOT - AI Chatbot Project

CIPHER BOT is an intelligent chatbot built with Python and Flask. It uses a local MySQL database for quick, predefined responses and integrates with the **Gemini API** to provide advanced, real-time query processing through powerful search grounding.

## ✨ Features

### Dual-Mode Operation:

* **Standard Mode:** Provides instant answers to common questions (like greetings, goodbyes, and help) by querying a local MySQL database for maximum speed.
* **Reasoning Mode (🧠):** Leverages the high-performance **Gemini 2.5 Flash** model via the Gemini API. This mode automatically uses **Google Search Grounding** to fetch and summarize current, real-time information for queries like "today's news" or "current weather."

### Core Components:

* **Conversation Logging:** All user messages and AI responses are saved to the database, linked to a default user.
* **Robust Backend:** Built with Flask, providing a stable and scalable web server.
* **Database Driven:** Uses MySQL to store user data, conversation history, and predefined "intents" for fast lookups.

## 🛠️ Tech Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Backend** | Python, Flask | Server and application logic |
| **Database** | MySQL | Data storage for conversations and intents |
| **Primary AI Model** | **Gemini 2.5 Flash** | Powers advanced reasoning and search-enabled responses |
| **API** | **Gemini API** (`v1beta` endpoint) | Provides access to the AI model and Search Grounding tool |
| **Libraries** | `Flask-CORS`, `mysql-connector-python`, `requests`, `python-dotenv` | Dependencies for server, database, and API calls |

## 🚀 How to Run This Project Locally

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

* **Python 3.8+**
* **Git**
* **MySQL Server:** Ensure you have a running MySQL instance with the correct credentials.

### 1. Clone the Repository

Clone this repository to your local machine:

```bash
git clone [https://github.com/your-username/cipher-chatbot.git](https://github.com/your-username/cipher-chatbot.git)
cd cipher-chatbot

project contributers ME, KAVISH , ISHAAN
