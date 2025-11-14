import requests
import json
import concurrent.futures

from logger_module import log_message
from ai_prompts import (
    PROMPT_MAP,
    PROMPT_SUPER_MAP,
    PROMPT_GENERAL_MAP,
    PROMPT_FINAL_MAP,
)

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3:8b-instruct-q4_K_M"


def generate_ollama_content(
    prompt, system_prompt, ai_type, temperature=0.3, history=None
):
    messages = []

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    if history:
        for role, message in history:
            ollama_role = "user" if role == "user" else "assistant"
            message_text = str(message) if message is not None else ""
            if message_text:
                messages.append({"role": ollama_role, "content": message_text})

    prompt_text = str(prompt) if prompt is not None else ""
    messages.append({"role": "user", "content": prompt_text})

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "options": {
            "temperature": temperature,
            "num_predict": 1024
        },
        "stream": False,
    }

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat", json=payload, timeout=120
        )
        response.raise_for_status()

        result = response.json()

        if "message" in result and "content" in result["message"]:
            return result["message"]["content"]
        else:
            return (
                f"ERROR: Respons tidak valid dari Ollama API untuk {ai_type}. Detail: {result}"
            )

    except requests.exceptions.RequestException as e:
        error_msg = f"ERROR saat memanggil Ollama API ({OLLAMA_URL}) untuk {ai_type}. Pastikan Ollama berjalan dan model '{OLLAMA_MODEL}' terinstal: {e}"
        log_message(prompt, error_msg, ai_type)
        return error_msg
    except Exception as e:
        error_msg = f"ERROR tak terduga dalam generate_ollama_content: {e}"
        log_message(prompt, error_msg, ai_type)
        return error_msg


def get_single_ai_response(
    prompt, ai_type, focus="Kode Baru", temp=0.7, history=None
):
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

    ai_response_text = generate_ollama_content(
        prompt, system_prompt, ai_type, temperature=temp, history=history
    )

    title_header = "Respon AI Tunggal"
    if ai_type == "General":
        title_header = "Respon AI General"
    elif ai_type in PROMPT_SUPER_MAP:
        title_header = "Respon AI Koding Cepat"

    return f"## 👑 {title_header} (Ollama: {ai_type})\n\n{ai_response_text}"


def get_combined_ai_response(original_prompt, focus="Kode Baru", temp=0.7, history=None):
    results = {}

    coding_ai_keys = list(PROMPT_MAP.keys())

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(coding_ai_keys)) as executor:
        future_to_ai = {
            executor.submit(
                generate_ollama_content,
                original_prompt,
                PROMPT_MAP[ai_type],
                ai_type,
                temp,
            ): ai_type
            for ai_type in coding_ai_keys
        }

        for future in concurrent.futures.as_completed(future_to_ai):
            ai_type = future_to_ai[future]
            try:
                results[ai_type] = future.result()
            except Exception as e:
                error_msg = (
                    f"ERROR saat menjalankan {ai_type} (Ollama) secara paralel: {e}"
                )
                log_message(original_prompt, error_msg, ai_type)
                results[ai_type] = error_msg

    intermediate_output = f"## Data Input Awal (Fokus: {focus}):\n{original_prompt}\n\n"
    intermediate_output += "## Hasil Analisis 3 AI:\n"

    for ai_type in coding_ai_keys:
        result_text = results.get(ai_type, "ERROR: Hasil tidak ditemukan.")
        intermediate_output += f"### {ai_type}\n{result_text}\n---\n"

    ai_final_type = "Keputusan Akhir (Final)"
    if focus == "Analisis Konsep":
        system_prompt_decision = PROMPT_FINAL_MAP["Analisis Konsep"].format(
            focus=focus
        )
    else:
        system_prompt_decision = PROMPT_FINAL_MAP["Koding"].format(focus=focus)

    final_decision_text = generate_ollama_content(
        intermediate_output,
        system_prompt_decision,
        ai_final_type,
        temperature=0.3,
        history=history,
    )

    final_output = f"## 👑 Keputusan Akhir (Ollama: {ai_final_type})\n\n"
    final_output += final_decision_text
    final_output += "\n\n***\n\n## 📋 Rincian Analisis (3 AI Awal)\n"

    for ai_type in coding_ai_keys:
        result_text = results.get(ai_type, "ERROR: Hasil tidak ditemukan.")
        final_output += f"### {ai_type}\n{result_text}\n\n---\n"

    log_message(original_prompt, final_output, "OLLAMA_COMBINED_4_AI")

    return final_output
