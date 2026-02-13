import requests
import concurrent.futures
import os
import time

from logger_module import log_message
from ai_prompts import PROMPT_MAP, PROMPT_SUPER_MAP, PROMPT_GENERAL_MAP, PROMPT_FINAL_MAP

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3:8b-instruct-q4_K_M")


def generate_ollama_content(prompt, system_prompt, ai_type, temperature=0.3, history=None):
    messages = []

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    if history:
        for role, msg in history:
            r = "user" if role == "user" else "assistant"
            if msg:
                messages.append({"role": r, "content": str(msg)})

    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "options": {"temperature": temperature, "num_predict": 2048},
        "stream": False,
    }

    # retry sederhana -- ollama lokal kadang timeout kalau model baru di-load
    for attempt in range(3):
        try:
            resp = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=150)
            resp.raise_for_status()
            data = resp.json()

            if "message" in data and data["message"].get("content"):
                return data["message"]["content"]

            return f"ERROR: Respons Ollama tidak valid untuk {ai_type}. Detail: {data}"

        except requests.exceptions.ConnectionError:
            return f"ERROR: Tidak bisa konek ke Ollama ({OLLAMA_URL}). Pastikan Ollama sudah jalan."
        except requests.exceptions.Timeout:
            if attempt < 2:
                log_message(prompt, f"Ollama timeout attempt {attempt+1}, retrying...", ai_type)
                time.sleep(2)
                continue
            return f"ERROR: Ollama timeout setelah 3x percobaan."
        except requests.exceptions.RequestException as e:
            err = f"ERROR memanggil Ollama untuk {ai_type}: {e}"
            log_message(prompt, err, ai_type)
            return err
        except Exception as e:
            return f"ERROR tak terduga: {e}"

    return f"ERROR: Ollama gagal untuk {ai_type}."


def get_single_ai_response(prompt, ai_type, focus="Kode Baru", temp=0.7, history=None):
    sys_prompt = ""

    if ai_type in PROMPT_MAP:
        sys_prompt = PROMPT_MAP[ai_type]
    elif ai_type in PROMPT_SUPER_MAP:
        sys_prompt = PROMPT_SUPER_MAP[ai_type]
    elif ai_type in PROMPT_GENERAL_MAP:
        sys_prompt = PROMPT_GENERAL_MAP[ai_type]
    elif ai_type == "Keputusan Akhir (Final)":
        tpl = PROMPT_FINAL_MAP["Analisis Konsep"] if focus == "Analisis Konsep" else PROMPT_FINAL_MAP["Koding"]
        sys_prompt = tpl.format(focus=focus)
    else:
        err = f"Tipe AI '{ai_type}' tidak dikenali."
        log_message(prompt, err, ai_type)
        return err

    text = generate_ollama_content(prompt, sys_prompt, ai_type, temperature=temp, history=history)

    if ai_type == "General":
        header = "Respon AI General"
    elif ai_type in PROMPT_SUPER_MAP:
        header = "Respon AI Koding Cepat"
    else:
        header = "Respon AI Tunggal"

    return f"## 👑 {header} (Ollama: {ai_type})\n\n{text}"


def get_combined_ai_response(original_prompt, focus="Kode Baru", temp=0.7, history=None):
    results = {}
    ai_keys = list(PROMPT_MAP.keys())

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(ai_keys)) as pool:
        futures = {
            pool.submit(generate_ollama_content, original_prompt, PROMPT_MAP[k], k, temp): k
            for k in ai_keys
        }
        for f in concurrent.futures.as_completed(futures):
            k = futures[f]
            try:
                results[k] = f.result()
            except Exception as e:
                err = f"ERROR paralel {k} (Ollama): {e}"
                log_message(original_prompt, err, k)
                results[k] = err

    combined = f"## Data Input Awal (Fokus: {focus}):\n{original_prompt}\n\n## Hasil Analisis 3 AI:\n"
    for k in ai_keys:
        combined += f"### {k}\n{results.get(k, 'ERROR: tidak ada hasil')}\n---\n"

    tpl = PROMPT_FINAL_MAP["Analisis Konsep"] if focus == "Analisis Konsep" else PROMPT_FINAL_MAP["Koding"]
    final_text = generate_ollama_content(
        combined, tpl.format(focus=focus),
        "Keputusan Akhir (Final)", temperature=0.3, history=history,
    )

    output = f"## 👑 Keputusan Akhir (Ollama: AI Ke-4)\n\n{final_text}"
    output += "\n\n***\n\n## 📋 Rincian Analisis (3 AI Awal)\n"
    for k in ai_keys:
        output += f"### {k}\n{results.get(k, 'ERROR: tidak ada hasil')}\n\n---\n"

    log_message(original_prompt, output, "OLLAMA_COMBINED_4_AI")
    return output
