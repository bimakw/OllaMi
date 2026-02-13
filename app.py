import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

from ollama_client import get_combined_ai_response as ollama_combined, get_single_ai_response as ollama_single
from gemini_client import get_combined_ai_response as gemini_combined, get_single_ai_response as gemini_single
from logger_module import get_logs


st.set_page_config(layout="wide")
st.title("🤖 Asisten AI Universal (Ollama & Gemini)")


if "messages" not in st.session_state:
    st.session_state.messages = []
if "config" not in st.session_state:
    st.session_state.config = {
        "focus": "Kode Baru",
        "temperature": 0.7,
        "mode": "General",
        "ai_provider": "Ollama (Lokal)"
    }
if "task_type" not in st.session_state:
    st.session_state.task_type = "💬 Chat General" if st.session_state.config["mode"] == "General" else "💻 Koding & Analisis Kode"


def display_combined_ai_response(response_text):
    separator = "\n\n***\n\n## 📋 Rincian Analisis (3 AI Awal)\n"

    if "## 👑 Respon AI" in response_text and separator not in response_text:
        response_content = response_text.split("\n\n", 1)[-1]
        st.markdown(response_content)
        return

    if "## 👑 Keputusan Akhir" in response_text:
        st.markdown("### ✨ Keputusan Utama AI Gabungan")
        main_decision_part, detailed_analysis_part = response_text.split(separator, 1)
        main_decision_content = main_decision_part.split("\n\n", 1)[-1]

        st.info(main_decision_content)

        if detailed_analysis_part:
            with st.expander("🔍 Bandingkan Analisis Mendalam (Output Mentah 3 AI)"):
                st.code(detailed_analysis_part, language="markdown")
    else:
        st.write(response_text)

def clear_chat_history():
    st.session_state.messages = []


with st.sidebar:
    st.header("🛠️ Pengaturan & Kontrol")

    st.subheader("⚙️ Kontrol Aplikasi")
    st.button("🧹 Clear Semua Chat", on_click=clear_chat_history, type="primary", use_container_width=True)

    st.markdown("---")

    st.subheader("🤖 Pilih Provider AI")
    st.session_state.config["ai_provider"] = st.radio(
        "Pilih AI:",
        ["Ollama (Lokal)", "Gemini (Google AI)"],
        index=0 if st.session_state.config["ai_provider"] == "Ollama (Lokal)" else 1,
        help="Ollama berjalan di komputer Anda (cepat, offline). Gemini menggunakan API Google (butuh internet, pintar)."
    )

    st.markdown("---")

    st.subheader("🤖 Pilih Tipe Tugas")
    default_index = 0 if st.session_state.task_type == "💬 Chat General" else 1

    task_type = st.radio(
        "Pilih fokus utama:",
        ["💬 Chat General", "💻 Koding & Analisis Kode"],
        key="task_type",
        index=default_index
    )

    st.markdown("---")

    if task_type == "💻 Koding & Analisis Kode":
        st.subheader("🤖 Pilih Mode Koding")

        mode_options = [
            "⚡ Koding Cepat (1 AI)",
            "Gabungan Penuh (4 AI)",
            "Keputusan Akhir (Final)",
            "Saran 1: Review",
            "Saran 2: Linter",
            "Saran 3: Generator"
        ]

        if st.session_state.config["mode"] == "General":
            st.session_state.config["mode"] = "⚡ Koding Cepat (1 AI)"

        try:
            current_mode_index = mode_options.index(st.session_state.config["mode"])
        except ValueError:
            current_mode_index = 0
            st.session_state.config["mode"] = "⚡ Koding Cepat (1 AI)"

        st.session_state.config["mode"] = st.selectbox(
            "Mode Respon Koding:",
            options=mode_options,
            index=current_mode_index
        )
    else:
        st.session_state.config["mode"] = "General"
        st.info("Anda sedang dalam mode Chat General. Tanyakan apa saja!")


    st.markdown("---")
    st.subheader("💡 Konfigurasi AI")

    # fokus cuma ditampilin kalau mode gabungan atau final
    needs_focus = st.session_state.config["mode"] in ["Gabungan Penuh (4 AI)", "Keputusan Akhir (Final)"]

    if needs_focus:
        focus_options = ["Kode Baru", "Refactoring Kode", "Debug", "Analisis Konsep"]
        try:
            current_focus_index = focus_options.index(st.session_state.config["focus"])
        except ValueError:
            current_focus_index = 0
        st.session_state.config["focus"] = st.selectbox(
            "Fokus Output AI Koding:",
            options=focus_options,
            index=current_focus_index
        )

    st.session_state.config["temperature"] = st.slider(
        "Kreativitas (Temperature):",
        min_value=0.0, max_value=1.0,
        value=st.session_state.config["temperature"],
        step=0.1
    )

    st.markdown("---")

    st.subheader("📜 Riwayat Log")
    try:
        log_content = get_logs()
        with st.expander("Lihat Riwayat Log Aplikasi"):
            st.code(log_content, language="text")
    except Exception:
        st.warning("Pastikan `logger_module.py` tersedia dan memiliki fungsi `get_logs()`.")


st.subheader("💬 Ruang Obrolan AI")

for role, message in st.session_state.messages:
    if role == "user":
        st.chat_message("user").write(message)
    else:
        with st.chat_message("assistant"):
            display_combined_ai_response(message)


if prompt := st.chat_input("Tanyakan apa saja, atau masukkan kode Anda..."):

    st.session_state.messages.append(("user", prompt))
    st.chat_message("user").write(prompt)

    selected_provider = st.session_state.config["ai_provider"]
    selected_mode = st.session_state.config["mode"]
    selected_focus = st.session_state.config.get("focus", "Kode Baru")
    selected_temp = st.session_state.config.get("temperature", 0.7)
    current_history = st.session_state.messages[:-1]
    prompt_only = st.session_state.messages[-1][1]

    response = ""

    with st.status(f"Memproses '{selected_mode}' via '{selected_provider}'...", expanded=True) as status:

        if selected_provider == "Ollama (Lokal)":
            func_single = ollama_single
            func_combined = ollama_combined
        else:
            func_single = gemini_single
            func_combined = gemini_combined

        if selected_mode == "⚡ Koding Cepat (1 AI)":
            st.write(f"Memanggil AI Koding Cepat via {selected_provider}...")
            response = func_single(
                prompt_only,
                ai_type="Koding Cepat (1 AI)",
                focus=selected_focus,
                temp=selected_temp,
                history=current_history
            )

        elif "Gabungan Penuh" in selected_mode:
            st.write(f"Memanggil 4 AI Gabungan via {selected_provider}...")
            response = func_combined(
                prompt_only,
                focus=selected_focus,
                temp=selected_temp,
                history=current_history
            )

        else:
            ai_type = selected_mode
            st.write(f"Memanggil AI Tunggal ({ai_type}) via {selected_provider}...")

            ai_type_key = "Keputusan Akhir (Final)" if "Keputusan Akhir" in selected_mode else ai_type

            response = func_single(
                prompt_only,
                ai_type=ai_type_key,
                focus=selected_focus,
                temp=selected_temp,
                history=current_history
            )

        status.update(label=f"✅ Selesai! Respon dari {selected_provider} berhasil dibuat.", state="complete", expanded=False)


    st.session_state.messages.append(("assistant", response))

    with st.chat_message("assistant"):
        display_combined_ai_response(response)

    st.rerun()