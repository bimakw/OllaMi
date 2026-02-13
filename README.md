# OllaMi

**OllaMi (Ollama + Gemini)** — AI chat companion yang bisa jalan lokal pakai Ollama atau lewat Gemini API. Ada mode multi-agent yang nggabungin output dari beberapa AI buat dapetin jawaban yang lebih bagus.

![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen)
![Version](https://img.shields.io/badge/Version-v1.0.0-blue)

---

## Overview

Dua mode utama:
- **Offline** — pakai Ollama yang jalan di local, 100% private.
- **Online** — konek ke Gemini API via internet.

Mode koding punya fitur multi-agent: 3 AI (Review, Linter, Generator) jalan paralel, hasilnya dikasih ke AI ke-4 buat bikin keputusan akhir.

<img width="1909" height="958" alt="OllaMi Interface" src="https://github.com/user-attachments/assets/6510ef9d-b17d-4584-913e-26b1c4cf9e2e" />

## Tech Stack

- **Framework:** Streamlit
- **LLM:** Ollama (lokal), Google Gemini (API)
- **Default Model:** `llama3:8b-instruct-q4_K_M` (bisa ganti via env var `OLLAMA_MODEL`)
- **Python:** 3.10+

## Setup

```bash
git clone https://github.com/Jov1114/OllaMi.git
cd OllaMi
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### Ollama (Offline)

Install Ollama dari [ollama.com](https://ollama.com/), lalu pull model:

```bash
ollama pull llama3:8b-instruct-q4_K_M
```

### Gemini (Online)

Ambil API key dari [Google AI Studio](https://aistudio.google.com/), bikin file `.env`:

```
GEMINI_API_KEY=your_key_here
```

### Run

```bash
streamlit run app.py
```

## Environment Variables

| Variable | Default | Keterangan |
|----------|---------|------------|
| `GEMINI_API_KEY` | - | API key Google Gemini |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Model Gemini yang dipake |
| `OLLAMA_URL` | `http://localhost:11434` | URL Ollama server |
| `OLLAMA_MODEL` | `llama3:8b-instruct-q4_K_M` | Model Ollama |

## License

MIT
