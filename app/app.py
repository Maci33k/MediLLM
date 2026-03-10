import streamlit as st
import os
import time
from dotenv import load_dotenv
from utils.translations import TEXTS

st.set_page_config(
    page_title="MediScribe AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if 'current_note' not in st.session_state:
    st.session_state['current_note'] = ""
if 'ostatni_wynik' not in st.session_state:
    st.session_state['ostatni_wynik'] = None
if 'lang_code' not in st.session_state:
    st.session_state['lang_code'] = "PL"
if 'selected_model' not in st.session_state:
    st.session_state['selected_model'] = "Gemini 3 Flash Preview"

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
    st.title("MediScribe AI")
    
    jezyk_wybor = st.radio(
        "Language / Język:",
        options=["PL", "EN"],
        index=0 if st.session_state['lang_code'] == "PL" else 1,
        horizontal=True
    )
    st.session_state['lang_code'] = jezyk_wybor
    
    t = TEXTS[jezyk_wybor]
    
    st.markdown("---")
    st.markdown(f"### {t['sidebar_title']}")
    
    lista_modeli = [
        "Gemini 3 Flash Preview",
        "Gemini 2.5 Flash Lite",
        "Gemini 2.5 Pro",
        "Llama 3.1 8B (via Groq)",
        "Llama 3.3 70B (via Groq)"
    ]
    
    if st.session_state['selected_model'] in lista_modeli:
        obecny_indeks = lista_modeli.index(st.session_state['selected_model'])
    else:
        obecny_indeks = 0

    wybrany_model = st.selectbox(
        t['select_model'],
        options=lista_modeli,
        index=obecny_indeks
    )
    
    st.session_state['selected_model'] = wybrany_model
    

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