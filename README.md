# OllaMi 🤖✨

**OllaMi (Ollama + Gemini)** is your personal, locally-running AI coding companion. It leverages a powerful 4-agent synthesis model, powered by Ollama and Gemini, to provide comprehensive coding solutions and analysis.



![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen)
![Version](https://img.shields.io/badge/Version-v0.1.0-blue)
---

### 📍 Overview

OllaMi isn't just another chat interface. It's a structured, multi-agent system that provides a hybrid experience:

* **Offline Mode:** Uses your local Ollama instance for 100% private generation.
* **Online Mode:** Connects to the Gemini API for more powerful, context-aware responses.

It combines the outputs of multiple AI "specialists" to generate a final, high-quality response.


<img width="1909" height="958" alt="OllaMi Interface" src="https://github.com/user-attachments/assets/6510ef9d-b17d-4584-913e-26b1c4cf9e2e" />

### ✨ Features

* **Hybrid Mode (Online/Offline):** Switch between local-only (Ollama) and powerful online (Gemini) generation.
* **Multi-Agent Synthesis:** Uses a 4-step process (Analyze, Refine, Critique, Finalize) for superior code and text generation.
* **Lightweight & Fast:** Built on the highly-optimized `Llama-3-8B-Instruct` and can also use your Google AI API.
* **Simple Interface:** Clean and easy-to-use Streamlit UI.

### 🛠️ Tech Stack

* **Framework:** Streamlit
* **LLM Service:** Ollama (Local), Google Gemini (API)
* **Core Text Model:** `llama3:8b-instruct-q4_K_M` (or you can **change** the model **based on** your computer)
* **Language:** Python 3.10+

---

## 🚀 Getting Started

Follow these steps to get OllaMi running on your local machine.

### 1. Prerequisite: Install Ollama

OllaMi relies on the Ollama service running in the background for its offline mode.

1.  Go to **[ollama.com](https://ollama.com/)** and download the application for your OS (macOS, Windows, or Linux).
2.  Install it and ensure the Ollama service is running.

### 2. Clone & Install OllaMi

Next, clone the project repository and install its dependencies.

```bash
# 1. Clone this repository
git clone https://github.com/Jov1114/OllaMi.git

# 2. Navigate to the project directory
cd OllaMi

# 3. (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# 4. Install the required Python packages
pip install -r requirements.txt

```

### 3. Configure Your AI Models
This final step configures the "brains" of the operation.


A. For Offline Mode (Ollama)
Open your terminal and run this command to download the default local model:

```bash
ollama pull llama3:8b-instruct-q4_K_M
```
(Note: You can change this default model later in the ollama_client.py file)


B. For Online Mode (Gemini)
To enable the "Online Mode", OllaMi needs your Google AI API key.

 1. Get your free API key from Google AI Studio.

 2. In the OllaMi project folder (where you just ran pip install), create a new file named .env

 3. Open the .env file and add your API key exactly like this:
 ```bash
GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```

### 4. Running the Application

You're all set!

Make sure your Ollama application is running (for offline mode).

In your terminal (from the OllaMi directory), run the Streamlit app:


```bash
streamlit run app.py
```




