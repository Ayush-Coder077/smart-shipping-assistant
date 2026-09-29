import json

stats_tracker = {
    "total_llm_calls": 0,
    "input_tokens": 0,
    "output_tokens": 0,
    "estimated_cost_usd": 0.0
}

def log_llm_usage(in_tokens: int, out_tokens: int, rate_per_million: float = 0.15):
    """Updates total system execution cost metrics."""
    stats_tracker["total_llm_calls"] += 1
    stats_tracker["input_tokens"] += in_tokens
    stats_tracker["output_tokens"] += out_tokens
    stats_tracker["estimated_cost_usd"] += ((in_tokens + out_tokens) / 1_000_000) * rate_per_million

def dump_cost_summary():
    """Prints the final token run report for the required README audit logs."""
    print("\n================ COST & TOKEN AUDIT REPORT ================")
    print(json.dumps(stats_tracker, indent=4))
    print("===========================================================\n")
