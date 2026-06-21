import json
import asyncio
from typing import List, Dict, Any
import google.generativeai as genai
from app.core.config import settings
from pydantic import BaseModel, ValidationError

# Configure Gemini
genai.configure(api_key=settings.gemini_api_key)

class ClassificationResult(BaseModel):
    txn_id: str
    category: str

class BatchClassificationResponse(BaseModel):
    classifications: List[ClassificationResult]

VALID_CATEGORIES = [
    "Food", "Shopping", "Travel", "Transport", 
    "Utilities", "Cash Withdrawal", "Entertainment", "Other"
]

PROMPT_TEMPLATE = """
You are a financial transaction classification expert. 
Classify the following transactions into exactly one of these categories:
{categories}

Transactions to classify:
{transactions_json}

Return your response strictly as a JSON object matching this structure:
{{
  "classifications": [
    {{"txn_id": "id1", "category": "CategoryName"}},
    {{"txn_id": "id2", "category": "CategoryName"}}
  ]
}}
Do not include any markdown formatting, backticks, or other text outside the JSON.
"""

def build_prompt(transactions: List[Dict[str, Any]]) -> str:
    # We only send necessary fields to save tokens
    mini_txns = []
    for t in transactions:
        mini_txns.append({
            "txn_id": t.get("txn_id"),
            "merchant": t.get("merchant"),
            "amount": t.get("amount"),
            "notes": t.get("notes")
        })
    
    return PROMPT_TEMPLATE.format(
        categories=", ".join(VALID_CATEGORIES),
        transactions_json=json.dumps(mini_txns, indent=2)
    )

def parse_and_validate_response(response_text: str) -> List[Dict[str, str]]:
    text = response_text.strip()
    # Handle possible markdown backticks
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    
    try:
        data = json.loads(text)
        validated = BatchClassificationResponse(**data)
        
        results = []
        for item in validated.classifications:
            cat = item.category if item.category in VALID_CATEGORIES else "Other"
            results.append({"txn_id": item.txn_id, "category": cat})
        return results
    except (json.JSONDecodeError, ValidationError) as e:
        raise ValueError(f"Failed to parse or validate LLM response: {e}")

async def classify_transactions_batch(transactions: List[Dict[str, Any]], timeout: int = 30) -> List[Dict[str, str]]:
    if not transactions:
        return []

    prompt = build_prompt(transactions)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    try:
        # Wrap sync call in asyncio.wait_for to enforce timeout
        loop = asyncio.get_running_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(None, lambda: model.generate_content(prompt)),
            timeout=timeout
        )
        
        if not response.text:
            raise ValueError("Empty response from LLM")
            
        return parse_and_validate_response(response.text)
        
    except asyncio.TimeoutError:
        raise TimeoutError("Gemini API call timed out")
    except Exception as e:
        raise RuntimeError(f"Error during LLM classification: {str(e)}")

def classify_transactions_sync(transactions: List[Dict[str, Any]], timeout: int = 30) -> List[Dict[str, str]]:
    """Synchronous wrapper for Celery tasks."""
    return asyncio.run(classify_transactions_batch(transactions, timeout))
