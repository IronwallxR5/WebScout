"""
agent.py - Core Agent Logic for AI Research Assistant

This module contains the 4 core functions that power the Level 3 Search Agent:
1. plan_research() - Breaks query into sub-queries
2. execute_search() - Calls Tavily API
3. filter_results() - Filters irrelevant results
4. generate_report() - Synthesizes final report with CODE-INJECTED citations
"""

import os
import re
from groq import Groq
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


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
    """Break down a user's vague query into 3 specific, searchable sub-queries."""
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """You are a research planning assistant. Your job is to break down 
a user's research question into exactly 3 specific, searchable sub-queries.

Each sub-query should:
- Be specific and focused
- Target different aspects of the main question
- Be optimized for web search (clear, concise keywords)

You MUST respond with valid JSON in this exact format:
{"queries": ["query1", "query2", "query3"]}"""
            },
            {
                "role": "user",
                "content": f"Break down this research question into 3 specific search queries:\n\n{query}"
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
    )
    
    import json
    result = json.loads(completion.choices[0].message.content)
    
    return result["queries"]


# ============================================================
# Function 2: Execute Search
# ============================================================

def execute_search(queries: list[str]) -> list[dict]:
    """Execute web searches using the Tavily API."""
    from tavily import TavilyClient
    
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    all_results = []
    
    for query in queries:
        try:
            response = tavily.search(
                query=query,
                search_depth="basic",
                max_results=5
            )
            
            for result in response.get("results", []):
                all_results.append({
                    "url": result.get("url", ""),
                    "title": result.get("title", ""),
                    "content": result.get("content", ""),
                    "query": query 
                })
                
        except Exception as e:
            print(f"Error searching for '{query}': {str(e)}")
            continue
    
    return all_results


# ============================================================
# Function 3: Filter Results (The "Student Advantage")
# ============================================================

class RelevanceCheck(BaseModel):
    """Structured output for relevance checking."""
    is_relevant: bool
    reason: str


def filter_results(query: str, raw_results: list[dict]) -> tuple[str, list[dict]]:
    """
    Filter out irrelevant search results using LLM judgment.
    
    Returns:
        A tuple of (context_string, sources_list)
        - context_string: ONLY numbered content for LLM (no titles/URLs!)
        - sources_list: List of {num, title, url} for citation injection
    """
    
    context_parts = []
    sources = []  # List of {"num": 1, "title": "...", "url": "..."}
    source_number = 1
    
    for result in raw_results:
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a relevance filter. Given a research question and 
a search result, determine if the result is relevant and useful for answering the question.

Be strict - only mark as relevant if the content directly helps answer the question.

Respond with valid JSON in this format:
{"is_relevant": true/false, "reason": "brief explanation"}"""
                    },
                    {
                        "role": "user",
                        "content": f"""Research Question: {query}

Search Result Title: {result.get('title', 'No title')}
Search Result Content: {result.get('content', '')[:1000]}

Is this result relevant to answering the research question?"""
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
            )
            
            import json
            relevance = json.loads(completion.choices[0].message.content)
            
            if relevance.get("is_relevant", False):
                url = result.get('url', '')
                title = result.get('title', 'Source')
                content = result.get('content', '')
                
                # Store source info for citation injection (title + url)
                sources.append({
                    "num": source_number,
                    "title": title,
                    "url": url
                })
                
                # Give LLM ONLY numbered content - NO titles or URLs!
                context_parts.append(f"[{source_number}]: {content}")
                source_number += 1
                
        except Exception as e:
            print(f"Error checking relevance: {str(e)}")
            url = result.get('url', '')
            title = result.get('title', 'Source')
            content = result.get('content', '')
            
            sources.append({
                "num": source_number,
                "title": title if title else "Source",
                "url": url
            })
            context_parts.append(f"[{source_number}]: {content}")
            source_number += 1
    
    context = "\n\n".join(context_parts)
    
    if len(context) > 15000:
        context = context[:15000] + "\n\n[Content truncated...]"
    
    return context, sources


# ============================================================
# Function 4: Generate Report with CODE-INJECTED Citations
# ============================================================

def generate_report(query: str, context: str, sources: list[dict]) -> str:
    """
    Generate a clean markdown report WITHOUT inline citations.
    Only adds a References section at the end.
    """
    
    if not context or context.strip() == "" or not sources:
        return """## ⚠️ Insufficient Information

I was unable to find enough relevant information to answer your question.

**Possible reasons:**
- The topic may be too niche or recent
- Search results were not relevant to your specific question
- The query may need to be rephrased

**Suggestions:**
- Try rephrasing your question with more specific keywords
- Break down complex questions into simpler parts
- Check if the topic has recent coverage online"""
    
    # Ask LLM to write a CLEAN report without any citations in the text
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """You are a research report writer.

RULES:
1. Write a comprehensive, well-structured answer to the research question
2. DO NOT include any citations, references, or source numbers in the text
3. Write clean, flowing prose without [1], [2], or any citation markers
4. Use markdown: ## for headers, **bold** for key terms, - for bullet points
5. DO NOT add a references or sources section - it will be added automatically
6. Just focus on explaining the topic clearly and thoroughly

EXAMPLE (CORRECT):
## What is a Computer?

A computer is an electronic device that processes data according to instructions. It can perform calculations, store information, and execute programs.

### Key Components

- **CPU**: The brain of the computer that executes instructions
- **Memory**: Stores data temporarily for quick access
- **Storage**: Saves data permanently"""
            },
            {
                "role": "user",
                "content": f"""Research Question: {query}

Source Information:
{context}

Write a comprehensive research report answering the question. Do NOT include any citations or reference numbers in the text. Just write clean, informative content."""
            }
        ],
        temperature=0.5,
    )
    
    report = completion.choices[0].message.content
    
    # Remove any citation patterns the LLM might have added anyway
    report = re.sub(r'\[\d+\]', '', report)
    report = re.sub(r'\[Source \d+\]', '', report)
    report = re.sub(r'\[[^\]]*\]\([^\)]*\)', '', report)  # Remove markdown links
    
    # Clean up extra spaces
    report = re.sub(r'  +', ' ', report)
    report = re.sub(r' +\.', '.', report)
    report = re.sub(r' +,', ',', report)
    
    # Append References section at the end
    references = "\n\n---\n\n## 📚 References\n\n"
    references += "The following sources were used to compile this report:\n\n"
    for source in sources:
        num = source["num"]
        title = source["title"]
        url = source["url"]
        if url:
            references += f"{num}. [{title}]({url})\n\n"
        else:
            references += f"{num}. {title}\n\n"
    
    return report + references
