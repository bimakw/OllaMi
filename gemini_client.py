import requests
import json
from logger_module import log_message
import concurrent.futures
import time
import os 

from ai_prompts import PROMPT_MAP, PROMPT_SUPER_MAP, PROMPT_GENERAL_MAP, PROMPT_FINAL_MAP

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


GEMINI_API_URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"

def generate_gemini_content(prompt, system_prompt, ai_type, temperature=0.3, history=None):
    """
    Memanggil Google Gemini API untuk menghasilkan konten.
    """
    
    if not GEMINI_API_KEY:
        return "ERROR: Environment variable 'GEMINI_API_KEY' tidak ditemukan. Harap atur environment variable Anda."

    api_url = f"{GEMINI_API_URL_BASE}?key={GEMINI_API_KEY}"
    
    headers = {
        'Content-Type': 'application/json'
    }

    contents = []
    if history:
        for role, message in history:
            gemini_role = "user" if role == "user" else "model"
            contents.append({"role": gemini_role, "parts": [{"text": str(message)}]})

    contents.append({"role": "user", "parts": [{"text": str(prompt)}]})

    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": 8192,
        },
        "safetySettings": [ 
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
    }

    if system_prompt:
        payload["systemInstruction"] = {
            "parts": [{"text": system_prompt}]
        }

    max_retries = 5
    delay = 1
    for attempt in range(max_retries):
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=180)
            
            if response.status_code == 429 or response.status_code >= 500:
                log_message(prompt, f"Gemini API attempt {attempt+1} failed with status {response.status_code}. Retrying in {delay}s...", ai_type)
                time.sleep(delay)
                delay *= 2
                continue

            response.raise_for_status()
            result = response.json()
            
            candidates = result.get('candidates', [])
            if candidates and candidates[0].get('content', {}).get('parts'):
                return candidates[0]['content']['parts'][0]['text']
            else:
                finish_reason = result.get('candidates', [{}])[0].get('finishReason', 'UNKNOWN')
                if finish_reason == 'SAFETY':
                    return f"ERROR: Respons Gemini diblokir karena alasan keamanan (SAFETY)."
                if response.status_code == 400 and "API_KEY_INVALID" in response.text:
                     return "ERROR: API Key Gemini yang Anda masukkan tidak valid. Silakan periksa kembali."
                return f"ERROR: Respons tidak valid dari Gemini API untuk {ai_type}. Detail: {result}"

        except requests.exceptions.RequestException as e:
            error_msg = f"ERROR saat memanggil Gemini API attempt {attempt+1}: {e}"
            log_message(prompt, error_msg, ai_type)
            if attempt == max_retries - 1:
                return error_msg
            time.sleep(delay)
            delay *= 2
        except Exception as e:
            error_msg = f"ERROR tak terduga dalam _generate_gemini_content: {e}"
            log_message(prompt, error_msg, ai_type)
            return error_msg
            
    return f"ERROR: Gagal memanggil Gemini API setelah {max_retries} percobaan."

def get_single_ai_response(prompt, ai_type, focus="Kode Baru", temp=0.7, history=None):
    """
    Mendapatkan respons dari satu jenis AI tertentu (GEMINI).
    """
    system_prompt = ""
    
    if ai_type in PROMPT_MAP:
        system_prompt = PROMPT_MAP[ai_type]
    elif ai_type in PROMPT_SUPER_MAP:
        system_prompt = PROMPT_SUPER_MAP[ai_type]
    elif ai_type in PROMPT_GENERAL_MAP:
        system_prompt = PROMPT_GENERAL_MAP[ai_type]
    elif ai_type == "Keputusan Akhir (Final)":
        if focus == "Analisis Konsep":
            system_prompt = PROMPT_FINAL_MAP["Analisis Konsep"].format(focus=focus)
        else:
            system_prompt = PROMPT_FINAL_MAP["Koding"].format(focus=focus)
    else:
        error_msg = f"Jenis AI '{ai_type}' tidak valid untuk mode tunggal."
        log_message(prompt, error_msg, ai_type)
        return error_msg

    
    ai_response_text = generate_gemini_content(
        prompt,
        system_prompt,
        ai_type,
        temperature=temp,
        history=history
    )

    title_header = "Respon AI Tunggal"
    if ai_type == "General":
        title_header = "Respon AI General"
    elif ai_type in PROMPT_SUPER_MAP:
        title_header = "Respon AI Koding Cepat"
        
    return f"## 👑 {title_header} (Gemini: {ai_type})\n\n{ai_response_text}"


def get_combined_ai_response(original_prompt, focus="Kode Baru", temp=0.7, history=None):
    """
    Menggabungkan respons dari empat jenis AI (GEMINI).
    """

    results = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_ai = {
            executor.submit(generate_gemini_content, original_prompt, PROMPT_MAP[ai_type], ai_type, temp): ai_type
            for ai_type in PROMPT_MAP.keys()
        }

        for future in concurrent.futures.as_completed(future_to_ai):
            ai_type = future_to_ai[future]
            try:
                results[ai_type] = future.result()
            except Exception as e:
                error_msg = f"ERROR saat menjalankan {ai_type} (Gemini) secara paralel: {e}"
                log_message(original_prompt, error_msg, ai_type)
                results[ai_type] = error_msg

    intermediate_output = f"## Data Input Awal (Fokus: {focus}):\n{original_prompt}\n\n"
    intermediate_output += "## Hasil Analisis 3 AI:\n"
    for ai_type in PROMPT_MAP:
        result_text = results.get(ai_type, "ERROR: Hasil tidak ditemukan.")
        intermediate_output += f"### {ai_type}\n{result_text}\n---\n"
    
    
    if focus == "Analisis Konsep":
        system_prompt_decision = PROMPT_FINAL_MAP["Analisis Konsep"].format(focus=focus)
    else:
        system_prompt_decision = PROMPT_FINAL_MAP["Koding"].format(focus=focus)
        
    final_decision_text = generate_gemini_content(
        intermediate_output,
        system_prompt_decision,
        "Keputusan Akhir (Final)",
        temperature=temp,
        history=history
    )

    final_output = f"## 👑 Keputusan Akhir (Gemini: AI Ke-4)\n\n"
    final_output += final_decision_text
    final_output += "\n\n***\n\n## 📋 Rincian Analisis (3 AI Awal)\n"

    for ai_type in PROMPT_MAP:
        result_text = results.get(ai_type, "ERROR: Hasil tidak ditemukan.")
        final_output += f"### {ai_type}\n{result_text}\n\n---\n"

    log_message(original_prompt, final_output, "GEMINI_COMBINED_4_AI")

    return final_output