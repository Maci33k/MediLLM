import streamlit as st
import time
import pandas as pd
import sys
import os
import json
import plotly.express as px
from pathlib import Path
import ast

# --- FIXING IMPORT PATH ---
main_dir = Path(__file__).parent.parent.resolve()
if str(main_dir) not in sys.path:
    sys.path.insert(0, str(main_dir))

# Imports from engine (Separated AI logic and Evaluator logic)
from utils.engine.ai_engine import analyze_note, load_patient_database
from utils.engine.evaluator import fuzzy_match, calculate_metrics_fuzzy, calculate_rouge_l, evaluate_text_llm
from utils.translations import TEXTS 

# --- RETRIEVING LANGUAGE FROM EXTERNAL TRANSLATIONS FILE ---
lang_code = st.session_state.get('lang_code', 'PL')
t = TEXTS.get(lang_code, TEXTS["PL"])
target_lang_str = "POLISH" if lang_code == "PL" else "ENGLISH"

st.set_page_config(page_title=t["lab_page_title"], page_icon="🧪", layout="wide")

if 'lab_results' not in st.session_state:
    st.session_state['lab_results'] = None

st.title(t["lab_title"])
st.caption(t["lab_caption"])

# --- SIDEBAR (ADVANCED SETTINGS) ---
with st.sidebar:
    st.header(t["lab_sidebar_header"])
    fuzzy_threshold = st.slider(t["lab_fuzzy_slider"], 0.4, 1.0, 0.65, 0.05)
    
    st.markdown("---")
    st.subheader(t["lab_methodology_subheader"])
    
    strategies_to_test = st.multiselect(
        t["lab_strategy_multiselect"],
        options=[
            "Standard (Baseline)",
            "Role-Playing",
            "Few-shot",
            "Chain of Thought"
        ],
        default=["Standard (Baseline)", "Chain of Thought"],
        help=t["lab_strategy_help"]
    )

    st.markdown("---")
    st.subheader("⚖️ Advanced Text Evaluation")
    use_llm_judge = st.checkbox("Enable LLM-as-a-Judge", value=False, help="An AI model will evaluate the medical accuracy of the text (0.0 - 1.0). Increases test duration.")
    st.markdown("---")
    st.subheader("📂 Load csv")
    uploaded_file = st.file_uploader("csv file", type=['csv'])
    
    if uploaded_file is not None:
        try:
            df_uploaded = pd.read_csv(uploaded_file, encoding='utf-8')
            
            # --- NAPRAWA STRINGIFIKACJI (Odtwarzanie list i słowników) ---
            for col in df_uploaded.columns:
                if df_uploaded[col].dtype == object:  # Jeśli kolumna to tekst
                    df_uploaded[col] = df_uploaded[col].apply(
                        lambda x: ast.literal_eval(x) if isinstance(x, str) and (x.strip().startswith('[') or x.strip().startswith('{')) else x
                    )
            # --------------------------------------------------------------

            st.session_state['lab_results'] = df_uploaded
            
            # Automatyczne wykrywanie, czy w pliku był użyty Sędzia AI
            if 'Summary_LLM' in df_uploaded.columns:
                st.session_state['used_llm_judge'] = True
            else:
                st.session_state['used_llm_judge'] = False
                
            st.success("✅ Wyniki pomyślnie wczytane! Wykresy zostały zaktualizowane.")
        except Exception as e:
            st.error(f"❌ Błąd podczas wczytywania pliku: {e}")

# --- MAIN SCREEN ---
all_models_list = [
    "Gemini 3.1 Flash Lite",
    "GPT-5 Mini",
    "Claude 4.5 Haiku",
    "Llama 4 Scout",
    "Gemini 3.1 Pro",
    "GPT-5.4",
    "Claude 4.6 Sonnet",
    "Llama 4 Maverick"
]

models_to_test = st.multiselect(t["lab_model_multiselect"], options=all_models_list, default=["Gemini 3.1 Flash Lite"])

col_n, col_delay = st.columns(2)
with col_n:
    n_samples = st.number_input(t["lab_doc_count"], min_value=1, max_value=20, value=3)
with col_delay:
    api_delay = st.slider(t["lab_api_delay"], 0.0, 5.0, 1.0)
    
st.markdown("---")

if st.button(t["lab_run_btn"], type="primary"):
    
    if not strategies_to_test:
        st.error(t["lab_err_no_strategy"])
        st.stop()
        
    if not models_to_test:
        st.error(t["lab_err_no_model"])
        st.stop()
        
    df_database = load_patient_database()
    gt_path = main_dir / "ground_truth.json"
    
    if df_database is None:
        st.error(t["lab_err_no_csv"])
        st.stop()
        
    if not gt_path.exists():
        st.error(t["lab_err_no_gt"])
        st.stop()
    
    with open(gt_path, "r", encoding="utf-8") as f:
        gt_dict = {item['id']: item['extraction'] for item in json.load(f)}

    available_ids = list(gt_dict.keys())
    sample_df = df_database[df_database.index.isin(available_ids)].head(int(n_samples))
    
    experiment_results = []
    progress_bar = st.progress(0)
    
    total_steps = len(models_to_test) * len(strategies_to_test) * len(sample_df)
    current_step = 0
    
    for active_model in models_to_test:
        for active_strategy in strategies_to_test:
            for i, (index, row) in enumerate(sample_df.iterrows()):
                original_text = row['transcription']
                
                start_time = time.time()
                print(t["lab_log_sending"].format(index=index, model=active_model, strategy=active_strategy))
                
                json_result = analyze_note(original_text, active_model, target_lang_str, prompt_strategy=active_strategy)
                
                duration = round(time.time() - start_time, 2)
                if json_result:
                    print(t["lab_log_success"].format(time=duration))
                else:
                    print(t["lab_log_error"].format(time=duration))
                print("-" * 50)
                
                chart_name = f"{active_model} ({active_strategy})"

                is_success = 1 if json_result and json_result.primary_diagnosis_technical != "ERROR: Extraction failed" else 0

                row_result = {
                    "Document_ID": index,
                    "Model": chart_name,
                    "Success": is_success,
                    "Source_Text": original_text,
                    "Execution_Time_sec": duration,
                    "Raw_Response": json_result.model_dump() if json_result else {"error": "Error"}
                }

                # 1. LIST EVALUATION (Fuzzy Match)
                list_categories = {
                    "Meds_Past": ("past_medications", "name"),
                    "Meds_Current": ("current_medications", "name"),
                    "Meds_Prescribed": ("prescribed_medications", "name"),
                    "History": ("medical_history", None),
                    "Findings": ("physical_findings", None)
                }

                for cat_name, (key, subkey) in list_categories.items():
                    gt_val = gt_dict[index].get(key, [])
                    gt_list = [x[subkey] if subkey else x for x in gt_val]
                    
                    if json_result:
                        raw_val = getattr(json_result, key, [])
                        ext_list = [getattr(x, subkey) if subkey else x for x in raw_val]
                        p, r, f1, jaccard_val = calculate_metrics_fuzzy(ext_list, gt_list, fuzzy_threshold)
                    else:
                        ext_list = []
                        p, r, f1, jaccard_val = 0, 0, 0, 0
                    
                    row_result.update({
                        f"{cat_name}_P": p, f"{cat_name}_R": r, f"{cat_name}_F1": f1, f"{cat_name}_Jaccard": jaccard_val,
                        f"{cat_name}_Obtained": ext_list,
                        f"{cat_name}_Expected": gt_list
                    })

                # 2. CONTINUOUS TEXT EVALUATION (ROUGE-L + LLM Judge)
                text_categories = {
                    "Summary": "patient_summary_target_lang",
                    "Plan": "clinical_plan",
                    "Instructions": "patient_instructions_target_lang"
                }

                for cat_name, key in text_categories.items():
                    gt_val = gt_dict[index].get(key, "")
                    llm_score = 0.0
                    
                    if json_result:
                        ext_val = getattr(json_result, key, "")
                        # ROUGE
                        p, r, f1 = calculate_rouge_l(ext_val, gt_val)
                        
                        # LLM JUDGE (Only if checkbox is checked)
                        if use_llm_judge:
                            llm_score = evaluate_text_llm(original_text, ext_val, cat_name, active_model)
                            time.sleep(1) # Protection against API rate-limiting
                    else:
                        ext_val = ""
                        p, r, f1 = 0.0, 0.0, 0.0
                    
                    row_result.update({
                        f"{cat_name}_ROUGE_P": p,
                        f"{cat_name}_ROUGE_R": r,
                        f"{cat_name}_ROUGE_F1": f1,
                        f"{cat_name}_LLM": llm_score,
                        f"{cat_name}_Obtained": ext_val,
                        f"{cat_name}_Expected": gt_val
                    })

                experiment_results.append(row_result)
                
                current_step += 1
                progress_bar.progress(current_step / total_steps)
                time.sleep(api_delay)
            
    st.session_state['lab_results'] = pd.DataFrame(experiment_results)
    st.session_state['used_llm_judge'] = use_llm_judge

if st.session_state['lab_results'] is not None:
    df = st.session_state['lab_results']
    used_judge = st.session_state.get('used_llm_judge', False)
    
    st.subheader(t["lab_agg_metrics_subheader"])
    df_agg = df.groupby('Model').mean(numeric_only=True).drop(columns=['Document_ID'], errors='ignore').reset_index()
    
    # Dynamic column list depending on LLM Judge usage
    cols_to_show = ['Model', 'Success', 'Meds_Current_F1', 'Meds_Prescribed_F1', 'History_F1', 'Findings_F1', 'Summary_ROUGE_F1', 'Plan_ROUGE_F1', 'Execution_Time_sec']
    if used_judge:
        cols_to_show.extend(['Summary_LLM', 'Plan_LLM', 'Instructions_LLM'])
        
    cols_to_show = [c for c in cols_to_show if c in df_agg.columns]
    st.dataframe(df_agg[cols_to_show].style.highlight_max(axis=0, color='#e1f5fe'))

    st.markdown("---")
    
    st.subheader(t["lab_detailed_subheader"])
    
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        doc_id = st.selectbox(t["lab_select_doc"], options=df['Document_ID'].unique())
    with col_sel2:
        mod_id = st.selectbox(t["lab_select_inspect"], options=df[df['Document_ID'] == doc_id]['Model'].unique())
    
    case = df[(df['Document_ID'] == doc_id) & (df['Model'] == mod_id)].iloc[0]
    
    with st.expander(t["lab_expander_source"]):
        st.text(case['Source_Text'])
        
    with st.expander(t["lab_expander_json"]):
        st.json(case['Raw_Response'])

    # --- SECTION 1: LISTS (FUZZY MATCHING) ---
    st.write("### 🔍 Entity Extraction (Fuzzy Matching)")
    categories_to_show = [
        ("Meds_Past", t["lab_cat_meds_past"]),
        ("Meds_Current", t["lab_cat_meds_current"]),
        ("Meds_Prescribed", t["lab_cat_meds_prescribed"]),
        ("History", t["lab_cat_history"]),
        ("Findings", t["lab_cat_findings"])
    ]

    for cat, full_name in categories_to_show:
        st.write(f"#### {full_name}")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Precision", case[f"{cat}_P"])
        m2.metric("Recall", case[f"{cat}_R"])
        m3.metric("F1 Score", case[f"{cat}_F1"])
        m4.metric("Jaccard", case[f"{cat}_Jaccard"]) 
        
        c_obt, c_exp = st.columns(2)
        with c_obt:
            st.markdown(t["lab_ai_obtained"])
            if case[f"{cat}_Obtained"]:
                for item in case[f"{cat}_Obtained"]:
                    is_correct, _ = fuzzy_match(item, case[f"{cat}_Expected"], threshold=st.session_state.get('fuzzy_threshold', 0.65))
                    color = "green" if is_correct else "red"
                    st.markdown(f"- :{color}[{item}]")
            else:
                st.write(t["lab_no_extracted"])
        
        with c_exp:
            st.markdown(t["lab_ground_truth"])
            if case[f"{cat}_Expected"]:
                for item in case[f"{cat}_Expected"]:
                    is_missing, _ = fuzzy_match(item, case[f"{cat}_Obtained"], threshold=st.session_state.get('fuzzy_threshold', 0.65))
                    color = "gray" if is_missing else "orange"
                    st.markdown(f"- :{color}[{item}]")
            else:
                st.write(t["lab_no_gt"])
        st.markdown("---")

    # --- SECTION 2: TEXTS (ROUGE-L & LLM JUDGE) ---
    st.write("### 📝 Text Generation (Quality Analysis)")
    texts_to_show = [
        ("Summary", "📄 Patient Summary"),
        ("Plan", "🏥 Clinical Plan"),
        ("Instructions", "✅ Instructions")
    ]

    for cat, full_name in texts_to_show:
        st.write(f"#### {full_name}")
        
        if used_judge:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("ROUGE-L Precision", case[f"{cat}_ROUGE_P"])
            m2.metric("ROUGE-L Recall", case[f"{cat}_ROUGE_R"])
            m3.metric("ROUGE-L F1 Score", case[f"{cat}_ROUGE_F1"])
            m4.metric("🧠 AI Judge (Faithfulness)", case[f"{cat}_LLM"])
        else:
            m1, m2, m3 = st.columns(3)
            m1.metric("ROUGE-L Precision", case[f"{cat}_ROUGE_P"])
            m2.metric("ROUGE-L Recall", case[f"{cat}_ROUGE_R"])
            m3.metric("ROUGE-L F1 Score", case[f"{cat}_ROUGE_F1"])
            
        c_obt, c_exp = st.columns(2)
        with c_obt:
            st.markdown(t["lab_ai_obtained"])
            st.info(case[f"{cat}_Obtained"] if case[f"{cat}_Obtained"] else "No text")
        with c_exp:
            st.markdown(t["lab_ground_truth"])
            st.success(case[f"{cat}_Expected"] if case[f"{cat}_Expected"] else "No text")
        st.markdown("---")

   # --- CHARTS ---
    st.subheader(t["lab_plot_subheader"])
    
    # Lista opcji
    chart_options = ["Meds_Current", "Meds_Prescribed", "Meds_Past", "History", "Findings", 
                     "Summary (ROUGE)", "Plan (ROUGE)", "Instructions (ROUGE)", "Performance (Latency)"]
    if used_judge:
        chart_options.extend(["Summary (LLM Judge)", "Plan (LLM Judge)", "Instructions (LLM Judge)"])
        
    chart_category = st.selectbox(t["lab_plot_select_cat"], options=chart_options)

    # Logika przygotowania danych do wykresu
    if "Performance (Latency)" in chart_category:
        prefix = "Execution_Time_sec"
        df_plot = df_agg[['Model', prefix]].copy()
        df_melted = pd.melt(df_plot, id_vars=['Model'], value_vars=[prefix], var_name='Metric', value_name='Score')
        df_melted['Metric'] = "Średni czas (sekundy)"
        color_map = ['#EA4335'] # Czerwony dla wydajności

    elif "(ROUGE)" in chart_category:
        base_cat = chart_category.split(" ")[0]
        prefix = f"{base_cat}_ROUGE"
        df_plot = df_agg[['Model', f'{prefix}_P', f'{prefix}_R', f'{prefix}_F1']].copy()
        df_melted = pd.melt(df_plot, id_vars=['Model'], value_vars=[f'{prefix}_P', f'{prefix}_R', f'{prefix}_F1'], var_name='Metric', value_name='Score')
        df_melted['Metric'] = df_melted['Metric'].replace({f'{prefix}_P': 'Precision', f'{prefix}_R': 'Recall', f'{prefix}_F1': 'F1 Score'})
        color_map = ['#4285F4', '#34A853', '#FBBC05']

    elif "(LLM Judge)" in chart_category:
        base_cat = chart_category.split(" ")[0]
        prefix = f"{base_cat}_LLM"
        df_plot = df_agg[['Model', prefix]].copy()
        df_melted = pd.melt(df_plot, id_vars=['Model'], value_vars=[prefix], var_name='Metric', value_name='Score')
        df_melted['Metric'] = "Accuracy Score (LLM)"
        color_map = ['#8E44AD']

    else:
        prefix = chart_category
        df_plot = df_agg[['Model', f'{prefix}_P', f'{prefix}_R', f'{prefix}_F1']].copy()
        df_melted = pd.melt(df_plot, id_vars=['Model'], value_vars=[f'{prefix}_P', f'{prefix}_R', f'{prefix}_F1'], var_name='Metric', value_name='Score')
        df_melted['Metric'] = df_melted['Metric'].replace({f'{prefix}_P': 'Precision', f'{prefix}_R': 'Recall', f'{prefix}_F1': 'F1 Score'})
        color_map = ['#4285F4', '#34A853', '#FBBC05']

    fig = px.bar(
        df_melted,
        x='Model',
        y='Score',
        color='Metric',
        barmode='group',
        title=f"Wyniki dla kategorii: {chart_category}",
        labels={'Score': 'Wartość / Czas', 'Model': 'Model AI'},
        color_discrete_sequence=color_map
    )
    y_range = [0, df_melted['Score'].max() * 1.2] if "Latency" in chart_category else [0, 1.1]
    fig.update_layout(yaxis=dict(range=y_range), xaxis_tickangle=-45)

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="CSV",
        data=csv_data,
        file_name='results.csv',
        mime='text/csv',
        type="primary"
    )