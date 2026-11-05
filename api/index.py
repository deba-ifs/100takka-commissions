from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from .parser import extract_commission_data_from_pdf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock Database for demonstration. Replace with DB calls (e.g., Supabase, MongoDB)
mock_db = [
    {"amc_name": "SBI Mutual Fund", "scheme_category": "Equity", "scheme_name": "SBI Bluechip Fund", "commission_rate": 0.75},
    {"amc_name": "HDFC Mutual Fund", "scheme_category": "Debt", "scheme_name": "HDFC Corporate Bond", "commission_rate": 0.40}
]

@app.get("/api/commissions")
def get_commissions():
    """Fetch all commission structures for the dashboard."""
    return {"status": "success", "data": mock_db}

@app.post("/api/upload")
async def upload_commission_pdf(file: UploadFile = File(...)):
    """Receives PDF, triggers Gemini extraction, and updates the database."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a PDF.")
    
    try:
        file_bytes = await file.read()
        
        # 1. Extract data
        extracted_data = extract_commission_data_from_pdf(file_bytes)
        
        if not extracted_data:
            raise HTTPException(status_code=500, detail="Failed to extract tabular data from PDF.")
        
        # 2. Save to Database (Mocked here by extending the list in memory)
        # IN PRODUCTION: Insert 'extracted_data' into your actual database.
        mock_db.extend(extracted_data)
        
        return {"status": "success", "message": f"Successfully processed {len(extracted_data)} schemes.", "data": extracted_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))