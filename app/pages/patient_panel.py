import streamlit as st
from utils.translations import TEXTS

lang_code = st.session_state.get('lang_code', 'PL')
t = TEXTS[lang_code]

st.set_page_config(page_title=t['pat_title'], page_icon="👤")

st.title(t['pat_title'])

if 'last_result' in st.session_state and st.session_state['last_result']:
    data = st.session_state['last_result']
    
    st.subheader(t['pat_summary_header'])
    st.info(data.patient_summary_target_lang)
    
    st.subheader(t['pat_instructions_header'])
    for instruction in data.patient_instructions_target_lang:
        st.write(f"- {instruction}")
else:
    st.warning(t['pat_no_data'])