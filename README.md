# OllaMi 🤖✨

**OllaMi (Ollama + Gemini)** is your personal, locally-running AI coding companion. It leverages a powerful 4-agent synthesis model, powered by Ollama and Gemini, to provide comprehensive coding solutions and analysis.

![OllaMi application screenshot](httpsimg.shields.io/badge/Python-3.10+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen)

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

### 2. Pull the Required AI Model (Ollama)

Open your terminal and run this command to download the default local model:

```bash
# Pull the fast, high-quality text model for coding
ollama pull llama3:8b-instruct-q4_K_M ( or other model you can cange it at OLLAMA_MODEL = "llama3:8b-instruct-q4_K_M" ( ollama_client.py ))

Clone & Install OllaMi
