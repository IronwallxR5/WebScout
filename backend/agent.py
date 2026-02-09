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
    Generate a markdown report and inject citations via code (not LLM).
    
    The LLM writes using [1], [2] references. Then Python code replaces
    those with proper markdown links [[Title](URL)].
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
    
    # Create source map for LLM prompt (just numbers, no titles!)
    source_numbers = ", ".join([f"[{s['num']}]" for s in sources])
    
    # Step 1: Ask LLM to write report using ONLY [1], [2], [3] citations
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": f"""You are a research report writer.

CRITICAL RULES:
1. Write a comprehensive answer to the research question
2. After EVERY fact or claim, add a citation using ONLY these formats: [1], [2], [3], etc.
3. You have these sources available: {source_numbers}
4. Do NOT write source names or titles - just use [1], [2], etc.
5. Use markdown: ## for headers, **bold** for key terms, - for bullets
6. Do NOT add a references section - it will be added automatically

EXAMPLE FORMAT:
Computers are electronic devices that process data [1]. They were first invented in the 20th century [2]. Modern computers can perform billions of calculations per second [1][3]."""
            },
            {
                "role": "user",
                "content": f"""Research Question: {query}

Sources:
{context}

Write a comprehensive research report. Use [1], [2], [3], etc. after each fact."""
            }
        ],
        temperature=0.3,
    )
    
    report = completion.choices[0].message.content
    
    # Step 2: Use CODE to replace [1], [2] with [[Title](url)]
    for source in sources:
        num = source["num"]
        title = source["title"]
        url = source["url"]
        
        # Clean and shorten title
        clean_title = title.replace("[", "").replace("]", "").replace("(", "").replace(")", "")
        short_title = clean_title[:40] + "..." if len(clean_title) > 40 else clean_title
        
        # Create the markdown citation link
        if url:
            citation = f"[[{short_title}]({url})]"
        else:
            citation = f"[{short_title}]"
        
        # Replace [1], [2], etc. with the actual citation link
        # Handle various formats: [1], [1], [1][2], etc.
        pattern = rf'\[{num}\]'
        report = re.sub(pattern, citation, report)
    
    # Step 3: Append References section
    references = "\n\n---\n\n## 📚 References\n\n"
    for source in sources:
        num = source["num"]
        title = source["title"]
        url = source["url"]
        if url:
            references += f"{num}. [{title}]({url})\n\n"
        else:
            references += f"{num}. {title}\n\n"
    
    return report + references
