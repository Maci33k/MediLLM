import os
import json
import time 
import pandas as pd
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional

from google import genai
from groq import Groq

load_dotenv(override=True)

# --- SECURE API KEY RETRIEVAL ---
def get_api_key(key_name):
    key = os.getenv(key_name)
    if key and key.strip():
        return key.strip()
    try:
        val = st.secrets.get(key_name)
        if val:
            return str(val).strip()
    except Exception:
        pass
    return None

# --- DATA STRUCTURES (PYDANTIC) ---
class Medication(BaseModel):
    name: str = Field(description="Medication name")
    dosage: Optional[str] = Field(None, description="Dosage")
    route: Optional[str] = Field(None, description="Route")

class Demographics(BaseModel):
    age: Optional[int] = Field(None, description="Age")
    gender: Optional[str] = Field(None, description="Gender")

class MedicalExtraction(BaseModel):
    reasoning: Optional[str] = Field(
        None,
        description="STEP-BY-STEP THINKING: Use this field to write your thought process BEFORE extracting data. Analyze timelines for medications."
    )
    
    patient_demographics: Optional[Demographics] = Field(None, description="Patient demographics")
    primary_diagnosis_technical: Optional[str] = Field(None, description="Official medical diagnosis")
    medical_history: List[str] = Field(default_factory=list, description="List of chronic diseases")
    physical_findings: List[str] = Field(default_factory=list, description="Objective findings from exam")
    clinical_plan: Optional[str] = Field(None, description="Treatment plan and next steps")
    
    past_medications: List[Medication] = Field(default_factory=list, description="Discontinued or past medications")
    current_medications: List[Medication] = Field(default_factory=list, description="Currently taken medications")
    prescribed_medications: List[Medication] = Field(default_factory=list, description="New medications prescribed during this visit")
    
    patient_summary_target_lang: Optional[str] = Field(None, description="Simple summary for the patient")
    patient_instructions_target_lang: List[str] = Field(default_factory=list, description="Simple instructions")

def get_schema_instructions():
    return json.dumps(MedicalExtraction.model_json_schema(), indent=2)

# --- AI ENGINE (LLM INFERENCE) ---
def analyze_note(note_text, model_name, target_language="POLISH", prompt_strategy="Zero-shot"):
    if not model_name: model_name = "Gemini 3.1 Flash Lite"
        
    model_mapping = {
        # --- WAGA LEKKA (Szybka ekstrakcja) ---
        "Gemini 3.1 Flash Lite": {"provider": "openrouter", "api_name": "google/gemini-3.1-flash-lite-preview"},
        "GPT-5 Mini":            {"provider": "openrouter", "api_name": "openai/gpt-5-mini"},
        "Claude 4.5 Haiku":      {"provider": "openrouter", "api_name": "anthropic/claude-haiku-4.5"},
        "Llama 4 Scout":         {"provider": "openrouter", "api_name": "meta-llama/llama-4-scout"},

        # --- WAGA CIĘŻKA (Zaawansowane rozumowanie) ---
        "Gemini 3.1 Pro":        {"provider": "openrouter", "api_name": "google/gemini-3.1-pro-preview"},
        "GPT-5.4":               {"provider": "openrouter", "api_name": "openai/gpt-5.4"},
        "Claude 4.6 Sonnet":     {"provider": "openrouter", "api_name": "anthropic/claude-sonnet-4.6"},
        "Llama 4 Maverick":      {"provider": "openrouter", "api_name": "meta-llama/llama-4-maverick"}
    }

    model_info = model_mapping.get(model_name, model_mapping["Gemini 3.1 Flash Lite"])
    provider = model_info["provider"]
    api_name = model_info["api_name"]

    strategy_prompt = ""
    if prompt_strategy == "Standard (Baseline)":
        strategy_prompt = "Extract the medical information from the note into the provided JSON schema. Do not use the 'reasoning' field."
    elif prompt_strategy == "Role-Playing":
        strategy_prompt = "You are an expert Chief Medical Officer and a highly skilled clinical coder with 20 years of experience. Your task is to review this patient note with absolute precision and medical accuracy. Pay strict attention to the timeline of medications. Do not use the 'reasoning' field."
    elif prompt_strategy == "Few-shot":
        strategy_prompt = """Use the following example as a guide for your extraction:
EXAMPLE NOTE: "Patient is here for a follow-up. Stopped taking Claritin. Currently taking Aspirin. I will prescribe Nasonex today."
EXAMPLE BEHAVIOR:
- past_medications: "Claritin"
- current_medications: "Aspirin"
- prescribed_medications: "Nasonex"
Now process the real note with the same accuracy. Do not use the 'reasoning' field."""
    elif prompt_strategy == "Chain of Thought":
        strategy_prompt = "THINK STEP-BY-STEP. Before extracting any lists, you MUST use the 'reasoning' field to write out a short logical analysis.\nStep 1: Identify all mentions of drugs or procedures.\nStep 2: Assign a timeline to each (is it past? is it current? is it a new prescription?).\nStep 3: Only after this analysis, populate the medication lists."

    language_prompt = f"CRITICAL INSTRUCTION: The ENTIRE output JSON must be in {target_language} language.\nPROMPT ENGINEERING STRATEGY TO FOLLOW:\n{strategy_prompt}"

    max_retries = 3
    attempt = 0
    
    while attempt < max_retries:
        try:       
            if provider in ["gemini", "openrouter"]:
                api_key = get_api_key("OPENROUTER_API_KEY")
                
                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=api_key,
                )
                
                system_prompt = f"You are a medical assistant expert. RULES: {language_prompt}\nSCHEMA: {get_schema_instructions()}"
                
                completion = client.chat.completions.create(
                    model=api_name,
                    messages=[
                        {"role": "system", "content": system_prompt}, 
                        {"role": "user", "content": note_text}
                    ],
                    response_format={"type": "json_object"}, 
                    temperature=0.1
                )
                
                raw_content = completion.choices[0].message.content.strip()
                
                # --- BULLETPROOF JSON EXTRACTOR ---
                # Szukamy pierwszej '{' i ostatniej '}', aby zignorować znaczniki ```json
                start_idx = raw_content.find('{')
                end_idx = raw_content.rfind('}')
                
                if start_idx != -1 and end_idx != -1:
                    clean_json = raw_content[start_idx:end_idx+1]
                else:
                    clean_json = raw_content # Fallback, jeśli nie znalazł klamer
                    
                return MedicalExtraction.model_validate_json(clean_json)
                # -----------------------------------------

            elif provider == "groq":
                api_key = get_api_key("GROQ_API_KEY")
                client = Groq(api_key=api_key)
                system_prompt = f"You are a medical assistant expert. RULES: {language_prompt}\nSCHEMA: {get_schema_instructions()}"
                completion = client.chat.completions.create(
                    model=api_name,
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": note_text}],
                    response_format={"type": "json_object"}, temperature=0.1
                )
                return MedicalExtraction.model_validate_json(completion.choices[0].message.content)

        except Exception as e:
            attempt += 1
            
            if attempt >= max_retries:
                print(f"❌ KRYTYCZNY BŁĄD: Model {model_name} poddał się po {max_retries} próbach! Wpisuję 0 i idę dalej.")
                return MedicalExtraction(
                    reasoning=f"ERROR: Model failed to generate valid JSON after {max_retries} attempts.",
                    patient_demographics=Demographics(age=0, gender="Unknown"),
                    primary_diagnosis_technical="ERROR: Extraction failed",
                    medical_history=[],
                    physical_findings=[],
                    clinical_plan="ERROR: Extraction failed",
                    past_medications=[],
                    current_medications=[],
                    prescribed_medications=[],
                    patient_summary_target_lang="ERROR: Extraction failed",
                    patient_instructions_target_lang=[]
                )
            
            wait_time = min(attempt * 5, 60) 
            print(f"⚠️ Limit API lub błąd walidacji w {model_name} (Próba {attempt}/{max_retries}): {e}")
            print(f"⏳ Czekam {wait_time} sekund przed ponowną próbą...")
            time.sleep(wait_time)


# --- DATA HANDLING (Temporarily kept here to maintain app functionality) ---
@st.cache_data
def load_patient_database():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'mtsamples.csv')
    if not os.path.exists(file_path): file_path = 'mtsamples.csv'
    if not os.path.exists(file_path): return None
    df = pd.read_csv(file_path)
    return df.dropna(subset=['transcription'])

def get_random_note():
    try:
        df = load_patient_database()
        if df is None: return "⚠️ ERROR: File 'mtsamples.csv' not found."
        target_category = 'General Medicine'
        subset = df[df['medical_specialty'].str.contains(target_category, na=False)]
        if subset.empty: subset = df
        return subset.sample(1).iloc[0]['transcription']
    except Exception as e:
        return f"❌ Error while fetching random note: {e}"