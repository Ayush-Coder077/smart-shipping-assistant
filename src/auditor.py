import json
from openai import OpenAI
from src.utils import log_llm_usage

class CostAuditor:
    def __init__(self, api_key: str = "local-mock-key", base_url: str = "http://localhost:11434/v1"):
       
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = "llama3" 
        
    def audit_route(self, origin: str, destination: str, week_str: str, cost: float, history: float, context: str) -> dict:
        system_prompt = (
            "You are a logistics audit assistant. Determine if a shipping cost spike is justified by context data.\n"
            "RULES:\n"
            "1. If context text explicitly states a valid disruption affecting this route/timeframe, return 'justified'.\n"
            "2. If context lacks matching data, or states stable parameters, return 'unexplained'. Do not extrapolate.\n"
            "OUTPUT FORMAT:\n"
            "Return raw valid JSON only matching this schema exactly:\n"
            '{"verdict": "justified"/"unexplained", "matched_note_id": "ID string or empty", "reason": "Plain English summary string"}'
        )
        
        user_content = (
            f"Route: {origin} -> {destination}\nWeek: {week_str}\n"
            f"Cost: {cost:.4f} vs Historical Avg: {history:.4f}\n"
            f"Retrieved Context:\n{context}"
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.0, # Complete determinism lock
                response_format={"type": "json_object"}
            )
            
           
            in_t = response.usage.prompt_tokens if response.usage else 0
            out_t = response.usage.completion_tokens if response.usage else 0
            log_llm_usage(in_t, out_t)
            
            return json.loads(response.choices.message.content)
        except Exception as e:
            return {
                "verdict": "unexplained",
                "matched_note_id": "",
                "reason": "Safe fallback fallback executed. Execution processing anomaly."
            }
