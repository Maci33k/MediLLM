import difflib
import re
import time
import os
from dotenv import load_dotenv
from rouge_score import rouge_scorer
from openai import OpenAI
from groq import Groq
from utils.engine.ai_engine import get_api_key  # Importujemy wspólną funkcję

# --- WCZYTANIE PLIKU .ENV ---
load_dotenv(override=True)

def fuzzy_match(ext_item, gt_list, threshold=0.65):
    """Fuzzy matching algorithm."""
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
    """Calculates Precision, Recall, F1 Score, and Accuracy for lists."""
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

def calculate_rouge_l(extracted_text, gt_text):
    """
    Calculates the ROUGE-L metric for the generated text.
    Returns a tuple: (Precision, Recall, F1-Score)
    """
    if not extracted_text and not gt_text: return 1.0, 1.0, 1.0
    if not extracted_text and gt_text: return 0.0, 0.0, 0.0
    if extracted_text and not gt_text: return 0.0, 0.0, 0.0

    if isinstance(extracted_text, list):
        extracted_text = " ".join([str(x) for x in extracted_text])
    if isinstance(gt_text, list):
        gt_text = " ".join([str(x) for x in gt_text])

    extracted_text = str(extracted_text).strip()
    gt_text = str(gt_text).strip()

    if not extracted_text and not gt_text:
        return 1.0, 1.0, 1.0

    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    scores = scorer.score(gt_text, extracted_text)
    
    return round(scores['rougeL'].precision, 3), round(scores['rougeL'].recall, 3), round(scores['rougeL'].fmeasure, 3)    

def evaluate_text_llm(source_text, generated_text, category="Summary", model_name=None):
    """
    LLM-as-a-Judge: Evaluates texts with DYNAMIC criteria based on the section.
    Wersja oparta na Google Gemini 3.1 Flash Lite.
    """
    if not generated_text or len(str(generated_text).strip()) < 5:
        return 0.0
        
    if isinstance(generated_text, list):
        generated_text = " ".join([str(x) for x in generated_text])

    # --- DYNAMICZNE ZASADY SĘDZIEGO ---
    if category == "Summary":
        task_desc = "Score the Patient Summary. It should contain the main diagnosis and overview."
        rules = "- Missing primary diagnosis = -20\n    - Incorrect medication = -15\n    - Hallucinated info = -25"
    elif category == "Plan":
        task_desc = "Score the Clinical Plan. Focus ONLY on treatments, next steps, and medications."
        rules = "- Penalizing for missing diagnosis is FORBIDDEN here.\n    - Missing or incorrect treatment/medication = -20\n    - Hallucinated info = -25"
    elif category == "Instructions":
        task_desc = "Score the Patient Instructions. Focus ONLY on actionable advice and drug dosage for the patient."
        rules = "- Penalizing for missing diagnosis is FORBIDDEN here.\n    - Incorrect dosage or medication instruction = -25\n    - Hallucinated info = -25"
    else:
        task_desc = "Score the extracted text."
        rules = "- Hallucinated info = -25"

    judge_prompt = f"""
    You are a medical audit expert. Compare the following generated {category} against the original medical note.
    
    Original Note:
    {source_text}
    
    Generated {category}:
    {generated_text}
    
    Task: {task_desc}

    - Accuracy (0-40)
    - Completeness relative to what is expected in a {category} (0-30)
    - No hallucinations (0-30)

    Rules:
    {rules}

    Return ONLY a single integer number from 0 to 100 representing the final score. Do not add any text.
    """
    
    api_key = get_api_key("OPENROUTER_API_KEY")
    if not api_key: return 0.0
        
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    
    attempt = 0
    while True:
        try:
            print(f"🔍 Sędzia AI analizuje sekcję: {category}...") 
            response = client.chat.completions.create(
                model="openai/gpt-5.4",
                messages=[{"role": "user", "content": judge_prompt}],
                temperature=0.0,
                max_tokens=500
            )
            result_str = response.choices[0].message.content.strip()
            numbers = re.findall(r'\d+', result_str)
            if numbers:
                score = int(numbers[0])
                print(f"✅ Sędzia AI przyznał ocenę: {score}/100") 
                return min(max(score / 100.0, 0.0), 1.0)
            
            print("⚠️ Sędzia AI nie zwrócił poprawnej liczby.")
            return 0.0
        except Exception as e:
            attempt += 1
            wait_time = min(attempt * 5, 60)
            print(f"🧠 Sędzia AI czeka na limit (Próba {attempt}): {e}")
            print(f"⏳ Czekam {wait_time} sekund przed ponowną próbą oceny...")
            time.sleep(wait_time)