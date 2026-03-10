import streamlit as st
from utils.translations import TEXTS

lang_code = st.session_state.get('lang_code', 'PL')
t = TEXTS[lang_code]

st.set_page_config(page_title=t['pat_title'], page_icon="👤")

st.title(t['pat_title'])

if 'ostatni_wynik' in st.session_state and st.session_state['ostatni_wynik']:
    dane = st.session_state['ostatni_wynik']
    
    st.subheader(t['pat_summary_header'])
    st.info(dane.patient_summary_target_lang)
    
    st.subheader(t['pat_instructions_header'])
    for instr in dane.patient_instructions_target_lang:
        st.write(f"- {instr}")
else:
    st.warning(t['pat_no_data'])