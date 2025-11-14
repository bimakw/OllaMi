# OllaMi 🤖✨

**OllaMi (Ollama + Gemini)** is your personal, locally-running AI coding companion. It leverages a powerful 4-agent synthesis model, powered by Ollama and Gemini, to provide comprehensive coding solutions, analysis, and now... **visual understanding!**

![OllaMi Demo](httpsimg.shields.io/badge/Python-3.10+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-In%20Development-orange)

---

### 📍 Overview

OllaMi isn't just another chat interface. It's a structured, multi-agent system that runs entirely on your local machine. It combines the outputs of multiple AI "specialists" to generate a final, high-quality response.

And with multimodal support, you can now upload screenshots, diagrams, or mockups and have OllaMi understand them.

[Image of OllaMi application screenshot]
*(Suggestion: Add a screenshot or GIF of your Streamlit app here!)*

### ✨ Features

* **100% Local:** Runs entirely on your machine. No data leaves your computer.
* **Multi-Agent Synthesis:** Uses a 4-step process (Analyze, Refine, Critique, Finalize) for superior code and text generation.
* **Multimodal Vision:** 📸 **Upload images!** Ask questions about UI mockups, translate diagrams to code, or debug from a screenshot.
* **Lightweight & Fast:** Built on the highly-optimized `Llama-3-8B-Instruct` quantized model.
* **Simple Interface:** Clean and easy-to-use Streamlit UI.

### 🛠️ Tech Stack

* **Framework:** Streamlit
* **LLM Service:** Ollama
* **Core Text Model:** `llama3:8b-instruct-q4_K_M`
* **Vision Model:** `llava` (or other multimodal model)
* **Language:** Python 3.10+

---

## 🚀 Getting Started

Follow these steps to get OllaMi running on your local machine.

### 1. Prerequisite: Install Ollama

OllaMi relies on the Ollama service running in the background.

1.  Go to **[ollama.com](https://ollama.com/)** and download the application for your OS (macOS, Windows, or Linux).
2.  Install it and ensure the Ollama service is running.

### 2. Pull the Required AI Models

You need two types of models: one for text/coding and one for vision. Open your terminal and run:

```bash
# Pull the fast, high-quality text model for coding
ollama pull llama3:8b-instruct-q4_K_M

# Pull the multimodal model for image understanding
ollama pull llava:latest
