import json
import asyncio
from typing import Dict, Any, List
import google.generativeai as genai
from app.core.config import settings
from pydantic import BaseModel, ValidationError

genai.configure(api_key=settings.gemini_api_key)

class SummaryResponse(BaseModel):
    total_spend_inr: float
    total_spend_usd: float
    top_merchants: Any
    anomaly_count: int
    narrative: str
    risk_level: str

PROMPT_TEMPLATE = """
You are a financial analyst. Analyze these transaction statistics and provide a summary.

Data:
Total Spend INR: {total_inr}
Total Spend USD: {total_usd}
Anomaly Count: {anomaly_count}
Top Merchants: {top_merchants}

Return a strictly valid JSON object matching this schema:
{{
    "total_spend_inr": <float>,
    "total_spend_usd": <float>,
    "top_merchants": <array or dict>,
    "anomaly_count": <int>,
    "narrative": "<2-3 sentence spending narrative>",
    "risk_level": "<low/medium/high>"
}}
Do not include markdown backticks.
"""

async def generate_summary_async(stats: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
    prompt = PROMPT_TEMPLATE.format(
        total_inr=stats.get('total_inr', 0),
        total_usd=stats.get('total_usd', 0),
        anomaly_count=stats.get('anomaly_count', 0),
        top_merchants=json.dumps(stats.get('top_merchants', []))
    )
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    try:
        loop = asyncio.get_running_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(None, lambda: model.generate_content(prompt)),
            timeout=timeout
        )
        
        text = response.text.strip()
        if text.startswith("```json"): text = text[7:]
        if text.startswith("```"): text = text[3:]
        if text.endswith("```"): text = text[:-3]
        text = text.strip()

        data = json.loads(text)
        validated = SummaryResponse(**data)
        return validated.model_dump()
        
    except Exception as e:
        # Fallback to empty narrative if LLM fails
        return {
            "total_spend_inr": stats.get('total_inr', 0),
            "total_spend_usd": stats.get('total_usd', 0),
            "top_merchants": stats.get('top_merchants', []),
            "anomaly_count": stats.get('anomaly_count', 0),
            "narrative": "Summary generation failed.",
            "risk_level": "medium"
        }

def generate_summary_sync(stats: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
    return asyncio.run(generate_summary_async(stats, timeout))
