import datetime
LOG_HISTORY = ""

def log_message(prompt, response, ai_type):
    global LOG_HISTORY
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    short_prompt = prompt[:100] + "..." if len(prompt) > 100 else prompt
    
    if "ERROR" in response:
        status = "ERROR"
        log_detail = response
    else:
        status = "SUCCESS"
        log_detail = f"Respons diterima (panjang: {len(response)} karakter)."

    log_entry = (
        f"[{timestamp}] | STATUS: {status}\n"
        f"  TIPE AI: {ai_type}\n"
        f"  PROMPT: {short_prompt}\n"
        f"  DETAIL: {log_detail}\n"
        f"---------------------------------------------------\n"
    )
    
    LOG_HISTORY = log_entry + LOG_HISTORY

def get_logs():
    global LOG_HISTORY
    if not LOG_HISTORY:
        return "Log masih kosong."
    
    return LOG_HISTORY
