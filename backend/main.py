from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
import io
import os
import logging
from .manager import AnalysisManager
from .email_service import EmailService

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MarketAnalyzer")

app = FastAPI(title="AI Business Market Analyzer")

# CORS (Allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Managers
manager = AnalysisManager()
email_service = EmailService()

# --- Models ---
class IdeaRequest(BaseModel):
    niche: str

class MarketCheckRequest(BaseModel):
    idea: str
    include_email_analysis: bool = False

class EmailCampaignRequest(BaseModel):
    subject: str
    body_template: str
    recipients: Optional[List[str]] = None # If provided manually
    generate_recipients_for_niche: Optional[str] = None # If AI should find them

# --- Endpoints ---

@app.post("/api/generate-idea")
async def generate_idea(request: IdeaRequest):
    """
    Generates a business idea based on niche market trends.
    """
    try:
        result = await manager.generate_new_idea(request.niche)
        return result
    except Exception as e:
        logger.error(f"Error generating idea: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-market")
async def analyze_market(request: MarketCheckRequest):
    """
    Analyzes the market viability of a given business idea.
    """
    try:
        result = await manager.run_market_check(request.idea, request.include_email_analysis)
        return result
    except Exception as e:
        logger.error(f"Error analyzing market: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/email/send")
async def send_email_campaign(
    background_tasks: BackgroundTasks,
    subject: str = Form(...),
    body: str = Form(...),
    file: UploadFile = File(None),
    niche: str = Form(None)
):
    """
    Sends emails.
    - Input: Excel file (column 'Email') OR Niche (for AI generation).
    """
    recipients = []

    # 1. Handle File Input
    if file:
        try:
            contents = await file.read()
            df = pd.read_excel(io.BytesIO(contents))
            # Look for a column named 'Email' (case insensitive)
            email_col = next((col for col in df.columns if 'email' in col.lower()), None)
            if email_col:
                recipients = df[email_col].dropna().tolist()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid Excel file: {e}")

    # 2. Handle AI Generation (Mock/Best Effort)
    if not recipients and niche:
        # call email service generator (placeholder in our code)
        pass

    if not recipients:
        raise HTTPException(status_code=400, detail="No recipients provided via file or found via niche.")

    # 3. Send in Background (Long running task)
    background_tasks.add_task(email_service.send_bulk_emails, recipients, subject, body)

    return {"status": "queued", "recipient_count": len(recipients)}

@app.get("/api/email/check")
async def check_email_responses(subject_keyword: str):
    """
    Checks the configured email inbox for responses containing the subject keyword.
    """
    summary = await email_service.analyze_inbox_for_feedback(subject_keyword)
    return {"summary": summary}

# Serve Frontend
# Ensure directories exist
os.makedirs("frontend", exist_ok=True)
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
