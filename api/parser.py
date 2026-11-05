import os
import json
import google.generativeai as genai
from tempfile import NamedTemporaryFile

# Initialize Gemini (Requires GEMINI_API_KEY in Vercel environment variables)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def extract_commission_data_from_pdf(pdf_bytes: bytes) -> list:
    """
    Extracts unstructured commission data from a PDF and returns standardized JSON.
    """
    # Write bytes to a temporary file for the Gemini File API to read
    with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(pdf_bytes)
        temp_file_path = temp_pdf.name

    try:
        # Upload the PDF to Gemini
        sample_file = genai.upload_file(path=temp_file_path, display_name="Commission Structure")
        
        # We use Gemini 1.5 Pro for complex document reasoning
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")
        
        prompt = """
        You are a financial data extraction assistant. Analyze this mutual fund commission structure PDF.
        Extract all the schemes and their associated commission rates.
        Respond ONLY with a valid JSON array of objects. Do not include markdown formatting or backticks.
        Each object must strictly have these keys:
        - "amc_name" (String, infer from document context)
        - "scheme_category" (String, e.g., "Equity", "Debt", "Hybrid", "Liquid")
        - "scheme_name" (String)
        - "commission_rate" (Float, representing the upfront/trail percentage)
        """
        
        response = model.generate_content([sample_file, prompt])
        
        # Clean the response and parse JSON
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()
            
        return json.loads(raw_text)
        
    except Exception as e:
        print(f"Extraction Error: {e}")
        return []
    finally:
        # Cleanup temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)