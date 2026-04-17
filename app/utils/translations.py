TEXTS = {
    "PL": {
        "sidebar_title": "Ustawienia",
        "select_language": "Język / Language:",
        "select_model": "Wybierz model AI:",
        
        "main_title": "Witamy w systemie MedDoc AI",
        "main_goal_title": "### Cel systemu",
        "main_goal_text": """
        Aplikacja demonstracyjna pokazująca możliwości **Dużych Modeli Językowych (LLM)** w medycynie.
        System realizuje dwa kluczowe zadania:
        
        1.  **Dla Lekarza (Ekstrakcja Danych):** Automatyczna zamiana notatki w języku naturalnym na ustrukturyzowany format JSON.
        2.  **Dla Pacjenta (Edukacja):** Tłumaczenie skomplikowanego żargonu medycznego na prosty, zrozumiały język.
        3.  **Dla Badacza (Ewaluacja):** Porównywanie modeli oraz technik Prompt Engineeringu w jednym przebiegu.
        """,
        "status_title": "Status Konfiguracji",
        "status_ok": "✅ Klucz API wykryty.",
        "status_err": "❌ Błąd: Brak klucza API w pliku .env!",
        "start_title": "Jak zacząć?",
        "start_steps": """
        1. Przejdź do zakładki **Panel Lekarza** w menu po lewej.
        2. Wgraj lub wylosuj notatkę medyczną.
        3. Kliknij **Analizuj**.
        4. Przejdź do **Panelu Pacjenta**, aby zobaczyć wynik.
        5. Przejdź do **Laboratorium**, aby przeprowadzić ewaluację modeli.
        """,

        "doc_title": "Panel Lekarski: Analiza",
        "doc_input_header": "1. Dane Wejściowe",
        "doc_upload_label": "Wgraj plik (PDF, DOCX, TXT)",
        "doc_random_btn": "Wylosuj notatkę (Demo CSV)",
        "doc_manual_label": "Lub wpisz notatkę ręcznie:",
        "doc_analyze_btn": "Analizuj notatkę",
        "doc_results_header": "2. Wyniki Analizy",
        "doc_tab_diagnosis": "Diagnoza",
        "doc_tab_meds": "💊 Leki",
        "doc_tab_json": "⚙️ JSON",
        
        "pat_title": "Twój Portal Pacjenta",
        "pat_no_data": "Brak danych. Lekarz musi najpierw przeanalizować Twoją wizytę.",
        "pat_summary_header": "📄 Podsumowanie wizyty",
        "pat_instructions_header": "✅ Zalecenia",
        
        "ai_prompt_lang": "POLISH",

        # --- TŁUMACZENIA DLA LABORATORIUM ---
        "lab_page_title": "Laboratorium - MedDocAI",
        "lab_title": "🧪 Laboratorium",
        "lab_caption": "Porównywanie modeli oraz technik Prompt Engineeringu w jednym przebiegu",
        "lab_sidebar_header": "⚙️ Ustawienia Ewaluacji",
        "lab_fuzzy_slider": "Czułość dopasowania (Fuzzy)",
        "lab_methodology_subheader": "🧠 Metodyka Badawcza",
        "lab_strategy_multiselect": "Wybierz techniki Prompt Engineeringu do porównania:",
        "lab_strategy_help": "Możesz wybrać kilka strategii. Model wykona zadanie dla każdej z nich osobno.",
        "lab_model_multiselect": "Wybierz modele:",
        "lab_doc_count": "Ilość dokumentów (N):",
        "lab_api_delay": "Opóźnienie API (s):",
        "lab_run_btn": "Uruchom Pełne Badanie",
        "lab_err_no_strategy": "Błąd: Musisz wybrać przynajmniej jedną strategię Prompt Engineeringu!",
        "lab_err_no_model": "Błąd: Musisz wybrać przynajmniej jeden model AI!",
        "lab_err_no_csv": "Błąd: Nie znaleziono pliku bazy pacjentów (mtsamples.csv)!",
        "lab_err_no_gt": "Błąd: Nie znaleziono pliku ground_truth.json!",
        "lab_log_sending": "⏳ Wysyłam -> Dok ID: {index} | Model: {model} | Strategia: {strategy}...",
        "lab_log_success": "✅ Sukces (Czas: {time}s)",
        "lab_log_error": "❌ BŁĄD (Czas: {time}s)",
        "lab_agg_metrics_subheader": "📊 Zagregowane Metryki Średnie",
        "lab_detailed_subheader": "🔍 Szczegółowe Porównanie (Inspektor Osi Czasu)",
        "lab_select_doc": "Wybierz Dokument (ID):",
        "lab_select_inspect": "Wybierz Model/Strategię do inspekcji:",
        "lab_expander_source": "📄 Zobacz tekst źródłowy notatki",
        "lab_expander_json": "🤖 Zobacz pełną, surową odpowiedź AI (JSON)",
        "lab_cat_meds_past": "⏳ Leki z wywiadu / Odstawione (Past Medications)",
        "lab_cat_meds_current": "💊 Leki stałe (Current Medications)",
        "lab_cat_meds_prescribed": "📝 Nowe leki zalecone (Prescribed Medications)",
        "lab_cat_history": "📜 Historia chorób (Medical History)",
        "lab_cat_findings": "🔍 Objawy fizykalne (Physical Findings)",
        "lab_ai_obtained": "**✅ Uzyskane (AI Obtained):**",
        "lab_no_extracted": "*Brak wyciągniętych elementów.*",
        "lab_ground_truth": "**📌 Oczekiwane (Ground Truth):**",
        "lab_no_gt": "*Zbiór prawdy nie zakłada tu żadnych wyników.*",
        "lab_plot_subheader": "📈 Wykresy Porównawcze Modeli i Strategii",
        "lab_plot_desc": "Wizualizacja zagregowanych wyników dla wszystkich badanych przypadków.",
        "lab_plot_select_cat": "Wybierz kategorię do analizy:",
        "lab_plot_title": "Wydajność w kategorii: {cat}",
        "lab_plot_y_label": "Wartość metryki (0 - 1.0)",
        "lab_plot_x_label": "Model (Strategia)",
        "lab_plot_legend": "Metryki"
    },
    
    "EN": {
        "sidebar_title": "Settings",
        "select_language": "Language / Język:",
        "select_model": "Select AI Model:",
        
        "main_title": "Welcome to MedDoc AI",
        "main_goal_title": "### System Goal",
        "main_goal_text": """
        Demonstration application showcasing **Large Language Models (LLM)** in healthcare.
        The system performs two key tasks:
        
        1.  **For Doctor (Data Extraction):** Converting natural language notes into structured JSON format.
        2.  **For Patient (Education):** Translating complex medical jargon into simple, understandable language.
        3.  **For Researcher (Evaluation):** Comparing models and Prompt Engineering techniques in a single run.
        """,
        "status_title": "Configuration Status",
        "status_ok": "✅ Google Gemini API Key detected.",
        "status_err": "❌ Error: Missing API Key in .env file!",
        "start_title": "How to start?",
        "start_steps": """
        1. Go to **Doctor's Panel** in the sidebar.
        2. Upload or generate a medical note.
        3. Click **Analyze**.
        4. Go to **Patient's Portal** to see results.
        5. Go to **Laboratory** to compare models and Prompt Engineering techniques.
        """,

        "doc_title": "Doctor's Panel: Analysis",
        "doc_input_header": "1. Input Data",
        "doc_upload_label": "Upload file (PDF, DOCX, TXT)",
        "doc_random_btn": "Random Note (Demo CSV)",
        "doc_manual_label": "Or type note manually:",
        "doc_analyze_btn": "Analyze Note",
        "doc_results_header": "2. Analysis Results",
        "doc_tab_diagnosis": "📝 Diagnosis",
        "doc_tab_meds": "💊 Medications",
        "doc_tab_json": "⚙️ JSON",
        
        "pat_title": "Your Patient Portal",
        "pat_no_data": "No data. The doctor must analyze your visit first.",
        "pat_summary_header": "📄 Visit Summary",
        "pat_instructions_header": "✅ Instructions",
        
        "ai_prompt_lang": "ENGLISH",

        # --- TRANSLATIONS FOR LABORATORY ---
        "lab_page_title": "Laboratory - MedDoc AI",
        "lab_title": "Laboratory",
        "lab_caption": "Comparing models and Prompt Engineering techniques in a single run",
        "lab_sidebar_header": "⚙️ Evaluation Settings",
        "lab_fuzzy_slider": "Fuzzy Match Threshold",
        "lab_methodology_subheader": "🧠 Research Methodology",
        "lab_strategy_multiselect": "Select Prompt Engineering techniques to compare:",
        "lab_strategy_help": "You can select multiple strategies. The model will execute the task for each separately.",
        "lab_model_multiselect": "Select models:",
        "lab_doc_count": "Number of documents (N):",
        "lab_api_delay": "API Delay (s):",
        "lab_run_btn": "🚀 Run Full Evaluation",
        "lab_err_no_strategy": "Error: You must select at least one Prompt Engineering strategy!",
        "lab_err_no_model": "Error: You must select at least one AI model!",
        "lab_err_no_csv": "Error: Patients database file (mtsamples.csv) not found!",
        "lab_err_no_gt": "Error: ground_truth.json file not found!",
        "lab_log_sending": "⏳ Sending -> Doc ID: {index} | Model: {model} | Strategy: {strategy}...",
        "lab_log_success": "✅ Success (Time: {time}s)",
        "lab_log_error": "❌ ERROR (Time: {time}s)",
        "lab_agg_metrics_subheader": "📊 Aggregated Average Metrics",
        "lab_detailed_subheader": "🔍 Detailed Comparison (Timeline Inspector)",
        "lab_select_doc": "Select Document (ID):",
        "lab_select_inspect": "Select Model/Strategy to inspect:",
        "lab_expander_source": "📄 View source note text",
        "lab_expander_json": "🤖 View full raw AI response (JSON)",
        "lab_cat_meds_past": "⏳ Past/Discontinued Medications",
        "lab_cat_meds_current": "💊 Current Medications",
        "lab_cat_meds_prescribed": "📝 Prescribed Medications",
        "lab_cat_history": "📜 Medical History",
        "lab_cat_findings": "🔍 Physical Findings",
        "lab_ai_obtained": "**✅ AI Obtained:**",
        "lab_no_extracted": "*No items extracted.*",
        "lab_ground_truth": "**📌 Ground Truth:**",
        "lab_no_gt": "*Ground truth does not expect any results here.*",
        "lab_plot_subheader": "📈 Model and Strategy Comparison Charts",
        "lab_plot_desc": "Visualization of aggregated results for all tested cases.",
        "lab_plot_select_cat": "Select category to analyze:",
        "lab_plot_title": "Performance in category: {cat}",
        "lab_plot_y_label": "Metric Value (0 - 1.0)",
        "lab_plot_x_label": "Model (Strategy)",
        "lab_plot_legend": "Metrics"
    }
}