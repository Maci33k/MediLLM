# MediScribe AI (doc2patient)

A demo application showcasing the capabilities of Large Language Models (LLMs) in the medical field. The system supports doctors by automatically extracting data from a patient visit and generating an easy-to-understand summary for the patient.

## Prerequisites

To run the project, you need:
* Installed **Python 3.9+**
* API Keys:
  * **Google Gemini API Key** (for Gemini models)
  * **Groq API Key** (for Llama models)

## Step-by-step Installation

### 1. Cloning the repository or downloading the code
Navigate to the project folder in the terminal:
```bash
cd doc2patient
```

### 2. Creating a virtual environment (optional but recommended)
For Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

For macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installing required libraries
Run the following command in the main project directory (or ensure you install all of them):
```bash
pip install streamlit pandas plotly python-dotenv google-genai groq openai pypdf python-docx
```
*(Alternatively, if you have a `requirements.txt` file, run `pip install -r requirements.txt`)*

### 4. Configuring environment variables
Create a `.env` file in the main application folder (or inside the `app/` folder) where the `app.py` file is located.
Add your API keys to it according to the following scheme:

```env
GOOGLE_API_KEY=your_google_gemini_api_key
GROQ_API_KEY=your_groq_api_key
```

## Running the application

Make sure you are inside the `app` folder where the `app.py` file is located. Run the following command:

```bash
cd app
streamlit run app.py
```

A local address (e.g., `http://localhost:8501`) will appear in the terminal, which will automatically open in your browser.

## Project structure

* `app/app.py` - Main entry file for the Streamlit view
* `app/pages/` - Individual application views:
  * `doctor_panel.py` - Doctor's panel facilitating the loading and processing of medical notes
  * `patient_panel.py` - Patient's panel showing an accessible summary of the visit
  * `laboratorium.py` - Analytical module facilitating the comparison of models on a built-in dataset
* `app/utils/` - Helper files:
  * `ai_engine.py` - Logic for communication with Llama and Gemini models
  * `translations.py` - File with multilingual constants to support PL/EN versions
