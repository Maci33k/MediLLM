import streamlit as st
import io
from pypdf import PdfReader
from docx import Document

from utils.ai_engine import pobierz_losowa_notatke, analizuj_notatke
from utils.translations import TEXTS

lang_code = st.session_state.get('lang_code', 'PL')
t = TEXTS[lang_code]

st.set_page_config(page_title=t['doc_title'], page_icon="👨‍⚕️", layout="wide")

def wczytaj_tekst_z_pliku(uploaded_file):
    """Wyciąga surowy tekst z PDF, DOCX lub TXT"""
    tekst = ""
    try:
        if uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                tekst += page.extract_text() + "\n"
        
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(uploaded_file)
            for para in doc.paragraphs:
                tekst += para.text + "\n"
        
        elif uploaded_file.type == "text/plain":
            tekst = uploaded_file.getvalue().decode("utf-8")
            
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None
        
    return tekst

if 'current_note' not in st.session_state:
    st.session_state['current_note'] = ""

st.title(t['doc_title'])

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader(t['doc_input_header'])
    
    uploaded_file = st.file_uploader(
        t['doc_upload_label'],
        type=['pdf', 'docx', 'txt']
    )

    if uploaded_file is not None:
        wyciagniety_tekst = wczytaj_tekst_z_pliku(uploaded_file)
        if wyciagniety_tekst:
            st.session_state['current_note'] = wyciagniety_tekst
            st.success(f"File loaded: {uploaded_file.name}")

    if st.button(t.get('doc_random_btn', "🎲 Random Note (CSV)")):
        nowa_notatka = pobierz_losowa_notatke()
        if nowa_notatka:
            st.session_state['current_note'] = nowa_notatka
            st.rerun()

    notatka_input = st.text_area(
        t['doc_manual_label'],
        value=st.session_state['current_note'],
        height=400
    )
    st.session_state['current_note'] = notatka_input
    
    analizuj_btn = st.button(t['doc_analyze_btn'], type="primary")

with col2:
    st.subheader(t['doc_results_header'])
    
    if analizuj_btn and notatka_input:
        model_name = st.session_state.get('selected_model')
        
        target_lang = t['ai_prompt_lang']
        
        with st.spinner("AI working..."):
            wynik = analizuj_notatke(
                notatka_input,
                model_name,
                target_language=target_lang
            )
            
            if wynik:
                st.session_state['ostatni_wynik'] = wynik
                
                tab1, tab2, tab3 = st.tabs([
                    t['doc_tab_diagnosis'],
                    t['doc_tab_meds'],
                    t['doc_tab_json']
                ])
                
                with tab1:
                    st.write(f"**Diagnosis:** {wynik.primary_diagnosis_technical}")
                    st.write(f"**Plan:** {wynik.clinical_plan}")
                    with st.expander("History / Findings"):
                        st.write("**History:**")
                        st.write(wynik.medical_history)
                        st.write("**Findings:**")
                        st.write(wynik.physical_findings)

                with tab2:
                    if wynik.current_medications:
                        data_dicts = [
                            {"Med": m.name, "Dose": m.dosage, "Route": m.route}
                            for m in wynik.current_medications
                        ]
                        st.dataframe(data_dicts, use_container_width=True)
                    else:
                        st.warning("No medications found.")

                with tab3:
                    st.json(wynik.model_dump_json())
            else:
                st.error("AI returned no results. Check logs.")