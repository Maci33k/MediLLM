import streamlit as st
import time
import pandas as pd
import sys
import os
import json
import re
from pathlib import Path
import difflib
import plotly.express as px

katalog_glowny = Path(__file__).parent.parent.resolve()
if str(katalog_glowny) not in sys.path:
    sys.path.insert(0, str(katalog_glowny))

from utils.ai_engine import analizuj_notatke, wczytaj_baze_pacjentow

def fuzzy_match(ext_item, gt_list, threshold=0.65):
    ext_str = str(ext_item).lower().strip()
    best_match = None
    best_ratio = 0.0
    
    for gt_item in gt_list:
        gt_str = str(gt_item).lower().strip()
        if ext_str == gt_str:
            return True, gt_item
        if ext_str in gt_str or gt_str in ext_str:
            if len(ext_str) > 4 and len(gt_str) > 4:
                return True, gt_item
        ratio = difflib.SequenceMatcher(None, ext_str, gt_str).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = gt_item
            
    if best_ratio >= threshold:
        return True, best_match
    return False, None

def calculate_metrics_fuzzy(extracted_list, gt_list, threshold=0.65):
    if not gt_list and not extracted_list: return 1.0, 1.0, 1.0, 1.0
    if not gt_list and extracted_list: return 0.0, 1.0, 0.0, 0.0
    if gt_list and not extracted_list: return 1.0, 0.0, 0.0, 0.0

    tp = 0
    unmatched_gt = list(gt_list)
    
    for ext_item in extracted_list:
        is_match, matched_gt_item = fuzzy_match(ext_item, unmatched_gt, threshold)
        if is_match:
            tp += 1
            if matched_gt_item in unmatched_gt:
                unmatched_gt.remove(matched_gt_item)
                
    fp = len(extracted_list) - tp
    fn = len(unmatched_gt)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = tp / (tp + fp + fn) if (tp + fp + fn) > 0 else 0.0
    
    return round(precision, 3), round(recall, 3), round(f1, 3), round(accuracy, 3)

st.set_page_config(page_title="Laboratorium - MediScribe", page_icon="🧪", layout="wide")

if 'lab_results' not in st.session_state:
    st.session_state['lab_results'] = None

st.title("🧪 Laboratorium Benchmarkingowe v7.0 (Multi-Prompt)")
st.caption("Porównywanie modeli oraz technik Prompt Engineeringu w jednym przebiegu")

jezyk = st.session_state.get('lang_code', 'PL')
target_lang_str = "POLISH" if jezyk == "PL" else "ENGLISH"

with st.sidebar:
    st.header("⚙️ Ustawienia Ewaluacji")
    fuzzy_threshold = st.slider("Czułość dopasowania (Fuzzy)", 0.4, 1.0, 0.65, 0.05)
    
    st.markdown("---")
    st.subheader("🧠 Metodyka Badawcza")
    
    strategie_do_testu = st.multiselect(
        "Wybierz techniki Prompt Engineeringu do porównania:",
        options=[
            "Standard (Baseline)",
            "Role-Playing",
            "Few-shot",
            "Chain of Thought"
        ],
        default=["Standard (Baseline)", "Chain of Thought"],
        help="Możesz wybrać kilka strategii. Model wykona zadanie dla każdej z nich osobno."
    )

lista_wszystkich_modeli = ["Gemini 3 Flash Preview", "Gemini 2.5 Flash Lite", "Gemini 2.5 Pro", "Llama 3.1 8B (via Groq)", "Llama 3.3 70B (via Groq)"]
modele_do_testu = st.multiselect("Wybierz modele:", options=lista_wszystkich_modeli, default=["Llama 3.1 8B (via Groq)"])

col_n, col_delay = st.columns(2)
with col_n:
    n_probek = st.number_input("Ilość dokumentów (N):", min_value=1, max_value=20, value=3)
with col_delay:
    opoznienie = st.slider("Opóźnienie API (s):", 0.0, 5.0, 1.0)

if st.button("🚀 Uruchom Pełne Badanie", type="primary"):
    
    if not strategie_do_testu:
        st.error("Błąd: Musisz wybrać przynajmniej jedną strategię Prompt Engineeringu!")
        st.stop()
        
    if not modele_do_testu:
        st.error("Błąd: Musisz wybrać przynajmniej jeden model AI!")
        st.stop()
        
    df_baza = wczytaj_baze_pacjentow()
    gt_path = katalog_glowny / "ground_truth.json"
    
    if df_baza is None:
        st.error("Błąd: Nie znaleziono pliku bazy pacjentów (mtsamples.csv)!")
        st.stop()
        
    if not gt_path.exists():
        st.error("Błąd: Nie znaleziono pliku ground_truth.json!")
        st.stop()
    
    with open(gt_path, "r", encoding="utf-8") as f:
        gt_dict = {item['id']: item['extraction'] for item in json.load(f)}

    dostepne_ids = list(gt_dict.keys())
    probka = df_baza[df_baza.index.isin(dostepne_ids)].head(int(n_probek))
    
    wyniki_eksperymentu = []
    progress_bar = st.progress(0)
    
    total_steps = len(modele_do_testu) * len(strategie_do_testu) * len(probka)
    current_step = 0
    
    for aktywny_model in modele_do_testu:
        for aktywna_strategia in strategie_do_testu:
            for i, (index, row) in enumerate(probka.iterrows()):
                tekst_oryginalny = row['transcription']
                
                czas_start = time.time()
                print(f"[{time.strftime('%H:%M:%S')}] ⏳ Wysyłam -> Dok ID: {index} | Model: {aktywny_model} | Strategia: {aktywna_strategia}...")
                
                wynik_json = analizuj_notatke(tekst_oryginalny, aktywny_model, target_lang_str, prompt_strategy=aktywna_strategia)
                
                czas_trwania = round(time.time() - czas_start, 2)
                if wynik_json:
                    print(f"[{time.strftime('%H:%M:%S')}] ✅ Sukces (Czas: {czas_trwania}s)")
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] ❌ BŁĄD (Czas: {czas_trwania}s)")
                print("-" * 50)
                
                nazwa_wykresowa = f"{aktywny_model} ({aktywna_strategia})"

                row_result = {
                    "Document_ID": index,
                    "Model": nazwa_wykresowa,
                    "Success": 1 if wynik_json else 0,
                    "Source_Text": tekst_oryginalny,
                    "Raw_Response": wynik_json.model_dump() if wynik_json else {"error": "Błąd"}
                }

                kategorie = {
                    "Meds_Past": ("past_medications", "name"),
                    "Meds_Current": ("current_medications", "name"),
                    "Meds_Prescribed": ("prescribed_medications", "name"),
                    "History": ("medical_history", None),
                    "Findings": ("physical_findings", None)
                }

                for kat_name, (key, subkey) in kategorie.items():
                    gt_val = gt_dict[index].get(key, [])
                    gt_list = [x[subkey] if subkey else x for x in gt_val]
                    
                    if wynik_json:
                        raw_val = getattr(wynik_json, key, [])
                        ext_list = [getattr(x, subkey) if subkey else x for x in raw_val]
                        p, r, f1, acc = calculate_metrics_fuzzy(ext_list, gt_list, fuzzy_threshold)
                    else:
                        ext_list = []
                        p, r, f1, acc = 0, 0, 0, 0
                    
                    row_result.update({
                        f"{kat_name}_P": p, f"{kat_name}_R": r, f"{kat_name}_F1": f1, f"{kat_name}_Acc": acc,
                        f"{kat_name}_Obtained": ext_list,
                        f"{kat_name}_Expected": gt_list
                    })

                wyniki_eksperymentu.append(row_result)
                
                current_step += 1
                progress_bar.progress(current_step / total_steps)
                time.sleep(opoznienie)
            
    st.session_state['lab_results'] = pd.DataFrame(wyniki_eksperymentu)

if st.session_state['lab_results'] is not None:
    df = st.session_state['lab_results']
    
    st.subheader("📊 Zagregowane Metryki Średnie")
    df_agg = df.groupby('Model').mean(numeric_only=True).drop(columns=['Document_ID']).reset_index()
    cols_to_show = ['Model', 'Success', 'Meds_Current_F1', 'Meds_Prescribed_F1', 'History_F1', 'Findings_F1']
    cols_to_show = [c for c in cols_to_show if c in df_agg.columns]
    st.dataframe(df_agg[cols_to_show].style.highlight_max(axis=0, color='#e1f5fe'))

    st.markdown("---")
    
    st.subheader("🔍 Szczegółowe Porównanie (Inspektor Osi Czasu)")
    
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        doc_id = st.selectbox("Wybierz Dokument (ID):", options=df['Document_ID'].unique())
    with col_sel2:
        mod_id = st.selectbox("Wybierz Model/Strategię do inspekcji:", options=df[df['Document_ID'] == doc_id]['Model'].unique())
    
    case = df[(df['Document_ID'] == doc_id) & (df['Model'] == mod_id)].iloc[0]
    
    with st.expander("📄 Zobacz tekst źródłowy notatki"):
        st.text(case['Source_Text'])
        
    with st.expander("🤖 Zobacz pełną, surową odpowiedź AI (JSON)"):
        st.json(case['Raw_Response'])

    categories_to_show = [
        ("Meds_Past", "⏳ Leki z wywiadu / Odstawione (Past Medications)"),
        ("Meds_Current", "💊 Leki stałe (Current Medications)"),
        ("Meds_Prescribed", "📝 Nowe leki zalecone (Prescribed Medications)"),
        ("History", "📜 Historia chorób (Medical History)"),
        ("Findings", "🔍 Objawy fizykalne (Physical Findings)")
    ]

    for kat, full_name in categories_to_show:
        st.write(f"#### {full_name}")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Precision", case[f"{kat}_P"])
        m2.metric("Recall", case[f"{kat}_R"])
        m3.metric("F1 Score", case[f"{kat}_F1"])
        m4.metric("Accuracy", case[f"{kat}_Acc"])
        
        c_obt, c_exp = st.columns(2)
        with c_obt:
            st.markdown("**✅ Uzyskane (AI Obtained):**")
            if case[f"{kat}_Obtained"]:
                for item in case[f"{kat}_Obtained"]:
                    is_correct, _ = fuzzy_match(item, case[f"{kat}_Expected"], threshold=st.session_state.get('fuzzy_threshold', 0.65))
                    color = "green" if is_correct else "red"
                    st.markdown(f"- :{color}[{item}]")
            else:
                st.write("*Brak wyciągniętych elementów.*")
        
        with c_exp:
            st.markdown("**📌 Oczekiwane (Ground Truth):**")
            if case[f"{kat}_Expected"]:
                for item in case[f"{kat}_Expected"]:
                    is_missing, _ = fuzzy_match(item, case[f"{kat}_Obtained"], threshold=st.session_state.get('fuzzy_threshold', 0.65))
                    color = "gray" if is_missing else "orange"
                    st.markdown(f"- :{color}[{item}]")
            else:
                st.write("*Zbiór prawdy nie zakłada tu żadnych wyników.*")
        st.markdown("---")

    st.subheader("📈 Wykresy Porównawcze Modeli i Strategii")
    st.write("Wizualizacja zagregowanych wyników dla wszystkich badanych przypadków.")

    kategoria_wykres = st.selectbox(
        "Wybierz kategorię do analizy:",
        options=["Meds_Current", "Meds_Prescribed", "Meds_Past", "History", "Findings"],
        format_func=lambda x: dict(categories_to_show).get(x, x)
    )

    df_plot = df_agg[['Model', f'{kategoria_wykres}_P', f'{kategoria_wykres}_R', f'{kategoria_wykres}_F1']].copy()
    
    df_melted = pd.melt(
        df_plot,
        id_vars=['Model'],
        value_vars=[f'{kategoria_wykres}_P', f'{kategoria_wykres}_R', f'{kategoria_wykres}_F1'],
        var_name='Metryka',
        value_name='Wynik'
    )
    
    df_melted['Metryka'] = df_melted['Metryka'].replace({
        f'{kategoria_wykres}_P': 'Precision',
        f'{kategoria_wykres}_R': 'Recall',
        f'{kategoria_wykres}_F1': 'F1 Score'
    })

    fig = px.bar(
        df_melted,
        x='Model',
        y='Wynik',
        color='Metryka',
        barmode='group',
        title=f"Wydajność w kategorii: {dict(categories_to_show).get(kategoria_wykres, kategoria_wykres)}",
        labels={'Wynik': 'Wartość metryki (0 - 1.0)', 'Model': 'Model (Strategia)'},
        color_discrete_sequence=['#4285F4', '#34A853', '#FBBC05']
    )
    
    fig.update_layout(
        yaxis=dict(range=[0, 1.1]),
        plot_bgcolor='rgba(0,0,0,0)',
        legend_title_text='Metryki',
        xaxis_tickangle=-45
    )

    st.plotly_chart(fig, use_container_width=True)