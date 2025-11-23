from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from services.research import search_viral_trends
from services.ai_agent import analyze_trend
from services.sourcing import find_aliexpress_links

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProductResult(BaseModel):
    id: int
    title: str
    snippet: str
    product_name: Optional[str] = None
    hype_score: int
    reason: str
    original_link: Optional[str] = None
    aliexpress_links: List[dict] = []

# In-memory storage for simplicity in this MVP
results_storage = []

@app.post("/api/scan", response_model=List[ProductResult])
def scan_trends():
    """
    1. Searches for viral trends.
    2. Analyzes them with AI.
    3. Returns the analyzed list.
    """
    global results_storage
    raw_trends = search_viral_trends()
    analyzed_results = []

    for idx, trend in enumerate(raw_trends):
        analysis = analyze_trend(trend)

        result = ProductResult(
            id=idx, # Simple ID generation
            title=trend['title'],
            snippet=trend['snippet'],
            original_link=trend.get('link'),
            product_name=analysis.get('product_name'),
            hype_score=analysis.get('hype_score', 0),
            reason=analysis.get('reason', 'No analysis available')
        )
        analyzed_results.append(result)

    results_storage = analyzed_results
    return analyzed_results

class SourceRequest(BaseModel):
    product_name: str

@app.post("/api/source")
def source_product(request: SourceRequest):
    """
    Finds AliExpress links for a given product name.
    """
    links = find_aliexpress_links(request.product_name)
    return {"links": links}

@app.get("/")
def read_root():
    return {"message": "Viral Product Finder API is running"}
