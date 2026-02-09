"""
agent.py - Core Agent Logic for AI Research Assistant

This module contains the 4 core functions that power the Level 3 Search Agent:
1. plan_research() - Breaks query into sub-queries
2. execute_search() - Calls Tavily API
3. filter_results() - Filters irrelevant results
4. generate_report() - Synthesizes final report
"""

import os
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ============================================================
# Pydantic Models for Structured LLM Outputs
# ============================================================

class ResearchPlan(BaseModel):
    """Structured output for research planning."""
    queries: list[str]


# ============================================================
# Function 1: Plan Research
# ============================================================

def plan_research(query: str) -> list[str]:
    """
    Break down a user's vague query into 3 specific, searchable sub-queries.
    
    Uses OpenAI's structured output feature with Pydantic to guarantee
    the response is a valid list of strings (no regex parsing needed).
    
    Args:
        query: The user's original research question
        
    Returns:
        A list of 3 specific search queries
    """
    
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """You are a research planning assistant. Your job is to break down 
a user's research question into exactly 3 specific, searchable sub-queries.

Each sub-query should:
- Be specific and focused
- Target different aspects of the main question
- Be optimized for web search (clear, concise keywords)

Example:
User: "Is AI dangerous?"
Sub-queries:
1. "AI safety risks and potential dangers 2024"
2. "Benefits of artificial intelligence for society"
3. "AI regulation and safety measures worldwide"
"""
            },
            {
                "role": "user",
                "content": f"Break down this research question into 3 specific search queries:\n\n{query}"
            }
        ],
        response_format=ResearchPlan,
    )
    
    # Extract the parsed Pydantic model
    research_plan = completion.choices[0].message.parsed
    
    return research_plan.queries


# ============================================================
# Function 2: Execute Search
# ============================================================

def execute_search(queries: list[str]) -> list[dict]:
    """
    Execute web searches using the Tavily API.
    
    Loops through all planned queries and collects search results.
    Handles errors gracefully to prevent one failed search from
    crashing the entire pipeline.
    
    Args:
        queries: List of search queries from plan_research()
        
    Returns:
        List of search results, each containing 'url' and 'content'
    """
    from tavily import TavilyClient
    
    # Initialize Tavily client
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    all_results = []
    
    for query in queries:
        try:
            # Execute search with Tavily
            response = tavily.search(
                query=query,
                search_depth="basic",  # Use "advanced" for deeper search
                max_results=5  # Get top 5 results per query
            )
            
            # Extract relevant fields from each result
            for result in response.get("results", []):
                all_results.append({
                    "url": result.get("url", ""),
                    "title": result.get("title", ""),
                    "content": result.get("content", ""),
                    "query": query  # Track which query found this result
                })
                
        except Exception as e:
            # Log error but continue with other queries
            print(f"Error searching for '{query}': {str(e)}")
            continue
    
    return all_results


# ============================================================
# Function 3: Filter Results (TODO) 
# ============================================================

def filter_results(query: str, raw_results: list[dict]) -> str:
    """Filter irrelevant results using LLM."""
    # TODO: Implement in next commit
    pass


# ============================================================
# Function 4: Generate Report (TODO)
# ============================================================

def generate_report(query: str, context: str) -> str:
    """Generate final markdown report."""
    # TODO: Implement in next commit
    pass
