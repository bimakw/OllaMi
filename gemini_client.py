import requests
import concurrent.futures
import time
import os

from logger_module import log_message
from ai_prompts import PROMPT_MAP, PROMPT_SUPER_MAP, PROMPT_GENERAL_MAP, PROMPT_FINAL_MAP

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


def generate_gemini_content(prompt, system_prompt, ai_type, temperature=0.3, history=None):
    if not GEMINI_API_KEY:
        return "ERROR: GEMINI_API_KEY belum di-set di environment."

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY,
    }

    contents = []
    if history:
        for role, msg in history:
            gemini_role = "user" if role == "user" else "model"
            contents.append({"role": gemini_role, "parts": [{"text": str(msg)}]})
    contents.append({"role": "user", "parts": [{"text": str(prompt)}]})

    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": 6144,
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ],
    }

    if system_prompt:
        payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}

    retries = 4
    wait = 1
    for attempt in range(retries):
        try:
            resp = requests.post(GEMINI_API_URL, headers=headers, json=payload, timeout=150)

            if resp.status_code == 429 or resp.status_code >= 500:
                log_message(prompt, f"Gemini attempt {attempt+1} gagal (HTTP {resp.status_code}), retry {wait}s...", ai_type)
                time.sleep(wait)
                wait *= 2
                continue

            resp.raise_for_status()
            data = resp.json()

            candidates = data.get("candidates", [])
            if candidates and candidates[0].get("content", {}).get("parts"):
                return candidates[0]["content"]["parts"][0]["text"]

            finish = candidates[0].get("finishReason", "UNKNOWN") if candidates else "NO_CANDIDATES"
            if finish == "SAFETY":
                return "ERROR: Respons diblokir oleh safety filter Gemini."
            return f"ERROR: Respons Gemini tidak valid untuk {ai_type}. finishReason={finish}"

        except requests.exceptions.RequestException as e:
            log_message(prompt, f"ERROR Gemini attempt {attempt+1}: {e}", ai_type)
            if attempt == retries - 1:
                return f"ERROR: Gagal memanggil Gemini setelah {retries}x: {e}"
            time.sleep(wait)
            wait *= 2
        except Exception as e:
            return f"ERROR: Unexpected error di generate_gemini_content: {e}"

    return f"ERROR: Gemini API gagal setelah {retries} percobaan."


def _resolve_system_prompt(ai_type, focus):
    if ai_type in PROMPT_MAP:
        return PROMPT_MAP[ai_type]
    if ai_type in PROMPT_SUPER_MAP:
        return PROMPT_SUPER_MAP[ai_type]
    if ai_type in PROMPT_GENERAL_MAP:
        return PROMPT_GENERAL_MAP[ai_type]
    if ai_type == "Keputusan Akhir (Final)":
        tpl = PROMPT_FINAL_MAP["Analisis Konsep"] if focus == "Analisis Konsep" else PROMPT_FINAL_MAP["Koding"]
        return tpl.format(focus=focus)
    return None


def get_single_ai_response(prompt, ai_type, focus="Kode Baru", temp=0.7, history=None):
    sys_prompt = _resolve_system_prompt(ai_type, focus)
    if sys_prompt is None:
        err = f"Tipe AI '{ai_type}' tidak dikenali."
        log_message(prompt, err, ai_type)
        return err

    text = generate_gemini_content(prompt, sys_prompt, ai_type, temperature=temp, history=history)

    if ai_type == "General":
        header = "Respon AI General"
    elif ai_type in PROMPT_SUPER_MAP:
        header = "Respon AI Koding Cepat"
    else:
        header = "Respon AI Tunggal"

    return f"## 👑 {header} (Gemini: {ai_type})\n\n{text}"


def get_combined_ai_response(original_prompt, focus="Kode Baru", temp=0.7, history=None):
    results = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures = {
            pool.submit(generate_gemini_content, original_prompt, PROMPT_MAP[k], k, temp): k
            for k in PROMPT_MAP
        }
        for f in concurrent.futures.as_completed(futures):
            k = futures[f]
            try:
                results[k] = f.result()
            except Exception as e:
                err = f"ERROR paralel {k} (Gemini): {e}"
                log_message(original_prompt, err, k)
                results[k] = err

    # gabungkan output 3 AI jadi input untuk AI ke-4
    combined = f"## Data Input Awal (Fokus: {focus}):\n{original_prompt}\n\n## Hasil Analisis 3 AI:\n"
    for k in PROMPT_MAP:
        combined += f"### {k}\n{results.get(k, 'ERROR: tidak ada hasil')}\n---\n"

    tpl = PROMPT_FINAL_MAP["Analisis Konsep"] if focus == "Analisis Konsep" else PROMPT_FINAL_MAP["Koding"]
    decision = generate_gemini_content(combined, tpl.format(focus=focus), "Keputusan Akhir (Final)", temperature=temp, history=history)

    output = f"## 👑 Keputusan Akhir (Gemini: AI Ke-4)\n\n{decision}"
    output += "\n\n***\n\n## 📋 Rincian Analisis (3 AI Awal)\n"
    for k in PROMPT_MAP:
        output += f"### {k}\n{results.get(k, 'ERROR: tidak ada hasil')}\n\n---\n"

    log_message(original_prompt, output, "GEMINI_COMBINED_4_AI")
    return output