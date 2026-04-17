import streamlit as st
import os
import time
from dotenv import load_dotenv
from utils.translations import TEXTS

st.set_page_config(
    page_title="MedDoc AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if 'current_note' not in st.session_state:
    st.session_state['current_note'] = ""
# ZMIANA: Zmieniono 'ostatni_wynik' na 'last_result' dla spójności całego projektu
if 'last_result' not in st.session_state:
    st.session_state['last_result'] = None
if 'lang_code' not in st.session_state:
    st.session_state['lang_code'] = "PL"
if 'selected_model' not in st.session_state:
    st.session_state['selected_model'] = "Gemini 3.1 Flash Lite"

with st.sidebar:
    st.title("MedDoc AI")
    
    lang_choice = st.radio(
        "Language / Język:",
        options=["PL", "EN"],
        index=0 if st.session_state['lang_code'] == "PL" else 1,
        horizontal=True
    )
    st.session_state['lang_code'] = lang_choice
    
    t = TEXTS[lang_choice]
    
    st.markdown("---")
    st.markdown(f"### {t['sidebar_title']}")
    
    models_list = [
        "Gemini 3.1 Flash Lite",
        "GPT-5 Mini",
        "Claude 4.5 Haiku",
        "Llama 4 Scout",
        "Gemini 3.1 Pro",
        "GPT-5.4",
        "Claude 4.6 Sonnet",
        "Llama 4 Maverick"
    ]
    
    if st.session_state['selected_model'] in models_list:
        current_index = models_list.index(st.session_state['selected_model'])
    else:
        current_index = 0

    chosen_model = st.selectbox(
        t['select_model'],
        options=models_list,
        index=current_index
    )
    
    st.session_state['selected_model'] = chosen_model
    

st.title(t['main_title'])

st.markdown(t['main_goal_title'])
st.markdown(t['main_goal_text'])
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader(t['status_title'])
    if api_key:
        st.success(t['status_ok'])
    else:
        st.error(t['status_err'])

with col2:
    st.subheader(t['start_title'])
    st.markdown(t['start_steps'])

st.markdown("---")