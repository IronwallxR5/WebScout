"""
main.py - FastAPI Application Entry Point

This module exposes the /api/research endpoint that orchestrates
the 4-step research pipeline: Plan → Search → Filter → Generate
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import plan_research, execute_search, filter_results, generate_report


app = FastAPI(
    title="AI Research Assistant",
    description="Level 3 Search Agent: Plans, Searches, Filters, and Synthesizes",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://web-scout-peach.vercel.app", 
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Request/Response Models
# ============================================================

class ResearchRequest(BaseModel):
    """Request body for research endpoint."""
    query: str


class ResearchResponse(BaseModel):
    """Response body for research endpoint."""
    status: str
    plan: list[str]
    report: str


# ============================================================
# API Endpoints
# ============================================================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "AI Research Assistant API is running"}


@app.post("/api/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    """
    Main research endpoint that orchestrates the 4-step pipeline.
    
    1. Plan: Break query into sub-queries
    2. Search: Execute web searches via Tavily
    3. Filter: Remove irrelevant results using LLM
    4. Generate: Synthesize final report
    
    Args:
        request: ResearchRequest containing the user's query
        
    Returns:
        ResearchResponse with status, research plan, and final report
    """
    
    try:
        # Step 1: Plan the research
        plan = plan_research(request.query)
        
        # Step 2: Execute searches
        raw_results = execute_search(plan)
        
        # Step 3: Filter irrelevant results
        context = filter_results(request.query, raw_results)
        
        # Step 4: Generate final report
        report = generate_report(request.query, context)
        
        return ResearchResponse(
            status="success",
            plan=plan,
            report=report
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Research failed: {str(e)}"
        )
