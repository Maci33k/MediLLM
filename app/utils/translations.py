
TEXTS = {
    "PL": {
        "sidebar_title": "Ustawienia",
        "select_language": "Język / Language:",
        "select_model": "Wybierz model AI:",
        
        "main_title": "🏥 Witamy w systemie MediScribe AI",
        "main_goal_title": "### Cel systemu",
        "main_goal_text": """
        Aplikacja demonstracyjna pokazująca możliwości **Dużych Modeli Językowych (LLM)** w medycynie.
        System realizuje dwa kluczowe zadania:
        
        1.  **👨‍⚕️ Dla Lekarza (Ekstrakcja Danych):** Automatyczna zamiana notatki w języku naturalnym na ustrukturyzowany format JSON.
        2.  **👤 Dla Pacjenta (Edukacja):** Tłumaczenie skomplikowanego żargonu medycznego na prosty, zrozumiały język.
        """,
        "status_title": "🛠️ Status Konfiguracji",
        "status_ok": "✅ Klucz API Google Gemini wykryty.",
        "status_err": "❌ Błąd: Brak klucza API w pliku .env!",
        "start_title": "🚀 Jak zacząć?",
        "start_steps": """
        1. Przejdź do zakładki **Panel Lekarza** w menu po lewej.
        2. Wgraj lub wylosuj notatkę medyczną.
        3. Kliknij **Analizuj**.
        4. Przejdź do **Panelu Pacjenta**, aby zobaczyć wynik.
        """,
        

        "doc_title": "👨‍⚕️ Panel Lekarski: Analiza",
        "doc_input_header": "1. Dane Wejściowe",
        "doc_upload_label": "📂 Wgraj plik (PDF, DOCX, TXT)",
        "doc_random_btn": "🎲 Wylosuj notatkę (Demo CSV)",
        "doc_manual_label": "Lub wpisz notatkę ręcznie:",
        "doc_analyze_btn": "🚀 Analizuj notatkę",
        "doc_results_header": "2. Wyniki Analizy",
        "doc_tab_diagnosis": "📝 Diagnoza",
        "doc_tab_meds": "💊 Leki",
        "doc_tab_json": "⚙️ JSON",
        
        "pat_title": "👤 Twój Portal Pacjenta",
        "pat_no_data": "Brak danych. Lekarz musi najpierw przeanalizować Twoją wizytę.",
        "pat_summary_header": "📄 Podsumowanie wizyty",
        "pat_instructions_header": "✅ Zalecenia",
        
        "ai_prompt_lang": "POLISH",
    },
    
    "EN": {
        "sidebar_title": "Settings",
        "select_language": "Language / Język:",
        "select_model": "Select AI Model:",
        
        "main_title": "🏥 Welcome to MediScribe AI",
        "main_goal_title": "### System Goal",
        "main_goal_text": """
        Demonstration application showcasing **Large Language Models (LLM)** in healthcare.
        The system performs two key tasks:
        
        1.  **👨‍⚕️ For Doctor (Data Extraction):** Converting natural language notes into structured JSON format.
        2.  **👤 For Patient (Education):** Translating complex medical jargon into simple, understandable language.
        """,
        "status_title": "🛠️ Configuration Status",
        "status_ok": "✅ Google Gemini API Key detected.",
        "status_err": "❌ Error: Missing API Key in .env file!",
        "start_title": "🚀 How to start?",
        "start_steps": """
        1. Go to **Doctor's Panel** in the sidebar.
        2. Upload or generate a medical note.
        3. Click **Analyze**.
        4. Go to **Patient's Portal** to see results.
        """,

        "doc_title": "👨‍⚕️ Doctor's Panel: Analysis",
        "doc_input_header": "1. Input Data",
        "doc_upload_label": "📂 Upload file (PDF, DOCX, TXT)",
        "doc_random_btn": "🎲 Random Note (Demo CSV)",
        "doc_manual_label": "Or type note manually:",
        "doc_analyze_btn": "🚀 Analyze Note",
        "doc_results_header": "2. Analysis Results",
        "doc_tab_diagnosis": "📝 Diagnosis",
        "doc_tab_meds": "💊 Medications",
        "doc_tab_json": "⚙️ JSON",
        
        "pat_title": "👤 Your Patient Portal",
        "pat_no_data": "No data. The doctor must analyze your visit first.",
        "pat_summary_header": "📄 Visit Summary",
        "pat_instructions_header": "✅ Instructions",
        
        "ai_prompt_lang": "ENGLISH",
    }
}