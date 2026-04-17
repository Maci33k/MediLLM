import streamlit as st
import io
from pypdf import PdfReader
from docx import Document

# Zaktualizowane importy do nowych, angielskich nazw w ai_engine
from utils.engine.ai_engine import get_random_note, analyze_note
from utils.translations import TEXTS

lang_code = st.session_state.get('lang_code', 'PL')
t = TEXTS[lang_code]

st.set_page_config(page_title=t['doc_title'], page_icon="👨‍⚕️", layout="wide")

def extract_text_from_file(uploaded_file):
    """Extracts raw text from PDF, DOCX, or TXT"""
    extracted_text = ""
    try:
        if uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                extracted_text += page.extract_text() + "\n"
        
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(uploaded_file)
            for para in doc.paragraphs:
                extracted_text += para.text + "\n"
        
        elif uploaded_file.type == "text/plain":
            extracted_text = uploaded_file.getvalue().decode("utf-8")
            
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None
        
    return extracted_text

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
        parsed_text = extract_text_from_file(uploaded_file)
        if parsed_text:
            st.session_state['current_note'] = parsed_text
            st.success(f"File loaded: {uploaded_file.name}")

    if st.button(t.get('doc_random_btn', "🎲 Random Note (CSV)")):
        new_note = get_random_note()
        if new_note:
            st.session_state['current_note'] = new_note
            st.rerun()

    note_input = st.text_area(
        t['doc_manual_label'],
        value=st.session_state['current_note'],
        height=400
    )
    st.session_state['current_note'] = note_input
    
    analyze_btn = st.button(t['doc_analyze_btn'], type="primary")

with col2:
    st.subheader(t['doc_results_header'])
    
    if analyze_btn and note_input:
        model_name = st.session_state.get('selected_model')
        
        target_lang = t['ai_prompt_lang']
        
        with st.spinner("AI working..."):
            result = analyze_note(
                note_input,
                model_name,
                target_language=target_lang
            )
            
            if result:
                # ZMIANA: Zmieniono klucz w session_state na angielski
                st.session_state['last_result'] = result
                
                tab1, tab2, tab3 = st.tabs([
                    t['doc_tab_diagnosis'],
                    t['doc_tab_meds'],
                    t['doc_tab_json']
                ])
                
                with tab1:
                    st.write(f"**Diagnosis:** {result.primary_diagnosis_technical}")
                    st.write(f"**Plan:** {result.clinical_plan}")
                    with st.expander("History / Findings"):
                        st.write("**History:**")
                        st.write(result.medical_history)
                        st.write("**Findings:**")
                        st.write(result.physical_findings)

                with tab2:
                    if result.current_medications:
                        data_dicts = [
                            {"Med": m.name, "Dose": m.dosage, "Route": m.route}
                            for m in result.current_medications
                        ]
                        st.dataframe(data_dicts, use_container_width=True)
                    else:
                        st.warning("No medications found.")

                with tab3:
                    st.json(result.model_dump_json())
            else:
                st.error("AI returned no results. Check logs.")