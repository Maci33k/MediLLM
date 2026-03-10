import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional
import streamlit as st
import pandas as pd

from google import genai
from groq import Groq
from openai import OpenAI

load_dotenv()

class Medication(BaseModel):
    name: str = Field(description="Nazwa leku / Medication name")
    dosage: Optional[str] = Field(None, description="Dawkowanie / Dosage")
    route: Optional[str] = Field(None, description="Droga podania / Route")

class Demographics(BaseModel):
    age: Optional[int] = Field(None, description="Wiek / Age")
    gender: Optional[str] = Field(None, description="Płeć / Gender")

class MedicalExtraction(BaseModel):
    reasoning: Optional[str] = Field(
        None,
        description="STEP-BY-STEP THINKING: Use this field to write your thought process BEFORE extracting data. Analyze timelines for medications."
    )
    
    patient_demographics: Demographics
    primary_diagnosis_technical: str = Field(..., description="Official medical diagnosis")
    medical_history: List[str] = Field(default_factory=list, description="List of chronic diseases")
    physical_findings: List[str] = Field(default_factory=list, description="Objective findings from exam")
    clinical_plan: str = Field(..., description="Treatment plan and next steps")
    
    past_medications: List[Medication] = Field(default_factory=list, description="Leki odstawione lub z historii")
    current_medications: List[Medication] = Field(default_factory=list, description="Leki stałe, kontynuowane")
    prescribed_medications: List[Medication] = Field(default_factory=list, description="Nowe leki zalecone na tej wizycie")
    
    patient_summary_target_lang: str = Field(..., description="Simple summary for the patient")
    patient_instructions_target_lang: List[str] = Field(default_factory=list, description="Simple instructions")

def get_schema_instructions():
    return json.dumps(MedicalExtraction.model_json_schema(), indent=2)

def analizuj_notatke(tekst_notatki, model_name, target_language="POLISH", prompt_strategy="Zero-shot"):
    if not model_name: model_name = "Gemini 3 Flash Preview"
        
    model_mapping = {
        "Gemini 3 Flash Preview": {"provider": "gemini", "api_name": "gemini-3-flash-preview"},
        "Gemini 2.5 Flash Lite":  {"provider": "gemini", "api_name": "gemini-2.5-flash-lite"},
        "Gemini 2.5 Pro":       {"provider": "gemini", "api_name": "gemini-2.5-pro"},
        "Llama 3.1 8B (via Groq)": {"provider": "groq",   "api_name": "llama-3.1-8b-instant"},
        "Llama 3.3 70B (via Groq)": {"provider": "groq", "api_name": "llama-3.3-70b-versatile"}
    }

    model_info = model_mapping.get(model_name.split(" (")[0], model_mapping["Gemini 3 Flash Preview"])
    provider = model_info["provider"]
    api_name = model_info["api_name"]

    strategy_prompt = ""
    
    if prompt_strategy == "Standard (Baseline)":
        strategy_prompt = """
        Extract the medical information from the note into the provided JSON schema.
        Do not use the 'reasoning' field.
        """
        
    elif prompt_strategy == "Role-Playing":
        strategy_prompt = """
        You are an expert Chief Medical Officer and a highly skilled clinical coder with 20 years of experience.
        Your task is to review this patient note with absolute precision and medical accuracy.
        Pay strict attention to the timeline of medications. Do not use the 'reasoning' field.
        """
    
    elif prompt_strategy == "Few-shot":
        strategy_prompt = """
        Use the following example as a guide for your extraction:
        EXAMPLE NOTE: "Patient is here for a follow-up. Stopped taking Claritin. Currently taking Aspirin. I will prescribe Nasonex today."
        EXAMPLE BEHAVIOR:
        - past_medications: "Claritin"
        - current_medications: "Aspirin"
        - prescribed_medications: "Nasonex"
        Now process the real note with the same accuracy. Do not use the 'reasoning' field.
        """
    
    elif prompt_strategy == "Chain of Thought":
        strategy_prompt = """
        THINK STEP-BY-STEP. Before extracting any lists, you MUST use the 'reasoning' field to write out a short logical analysis.
        Step 1: Identify all mentions of drugs or procedures.
        Step 2: Assign a timeline to each (is it past? is it current? is it a new prescription?).
        Step 3: Only after this analysis, populate the medication lists.
        """

    language_prompt = f"""
    CRITICAL INSTRUCTION: The ENTIRE output JSON must be in {target_language} language.
    PROMPT ENGINEERING STRATEGY TO FOLLOW:
    {strategy_prompt}
    """

    try:
        if provider == "gemini":
            api_key = os.getenv("GOOGLE_API_KEY")
            client = genai.Client(api_key=api_key)
            final_prompt = f"Analyze the following medical note.\n{language_prompt}\nNOTE:\n{tekst_notatki}"
            response = client.models.generate_content(
                model=api_name,
                contents=final_prompt,
                config={'response_mime_type': 'application/json', 'response_schema': MedicalExtraction},
            )
            return response.parsed

        elif provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            client = Groq(api_key=api_key)
            system_prompt = f"You are a medical assistant expert. RULES: {language_prompt}\nSCHEMA: {get_schema_instructions()}"
            completion = client.chat.completions.create(
                model=api_name,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": tekst_notatki}],
                response_format={"type": "json_object"}, temperature=0.1
            )
            return MedicalExtraction.model_validate_json(completion.choices[0].message.content)

        elif provider == "openai":
            pass

    except Exception as e:
        print(f"❌ Błąd w modelu {model_name}: {e}")
        return None

@st.cache_data
def wczytaj_baze_pacjentow():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'mtsamples.csv')
    
    if not os.path.exists(file_path):
        file_path = 'mtsamples.csv'
        
    if not os.path.exists(file_path):
        return None

    df = pd.read_csv(file_path)
    df = df.dropna(subset=['transcription'])
    return df

def pobierz_losowa_notatke():
    try:
        df = wczytaj_baze_pacjentow()
        
        if df is None:
            return "⚠️ BŁĄD: Nie znaleziono pliku 'mtsamples.csv'. Upewnij się, że plik leży w tym samym folderze co skrypt Pythona!"
            
        target_category = 'General Medicine'
        subset = df[df['medical_specialty'].str.contains(target_category, na=False)]
        
        if subset.empty:
            subset = df
            
        return subset.sample(1).iloc[0]['transcription']
        
    except Exception as e:
        return f"❌ Wystąpił błąd w losowaniu: {e}"