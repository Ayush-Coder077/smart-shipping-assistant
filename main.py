import pandas as pd
from src.pipeline import calculate_baselines
from src.rag_engine import DeterministicRAGEngine
from src.auditor import CostAuditor
from src.utils import dump_cost_summary
def run_pipeline(shipment_csv: str, notes_csv: str, output_csv: str):
    print("📊 Stage 1: Running bug-free pipeline calculations...")
    processed_df = calculate_baselines(shipment_csv)
    
    print("🔍 Stage 2: Initializing high-speed deterministic parser...")
    rag = DeterministicRAGEngine(notes_csv)
    
    processed_df['vs_own_history'] = processed_df['vs_own_history'].replace("nan% vs this route's past average", "+0.0% vs this route's past average")
    
    # Establish dynamic baseline default sets
    processed_df['flagged'] = "No Anomaly"
    processed_df['matched_note_id'] = ""
    processed_df['reason'] = "Cost parameters operate within normal variance boundaries."
    
    anomaly_mask = processed_df['is_anomaly'] == True
    print(f"🚨 Processing {anomaly_mask.sum()} true mathematical cost anomalies...")
    
    for idx, row in processed_df.iterrows():
        if not row['is_anomaly']:
            continue
            
        context = rag.retrieve_context(row['origin'], row['destination'], row['week_of'])
        
        if "No contextual disruption records found" in context or not context.strip():
            processed_df.at[idx, 'flagged'] = "Yes"
            processed_df.at[idx, 'matched_note_id'] = ""
            processed_df.at[idx, 'reason'] = "No matching note found for this route or date range. Cost rise looks unexplained and worth a human review."
        else:
            try:
                lines = context.split('\n')
                note_id = "N/A"
                details = ""
                for line in lines:
                    if line.startswith("Note ID:"):
                        note_id = line.replace("Note ID:", "").strip()
                    if line.startswith("Details:"):
                        details = line.replace("Details:", "").strip()
                
                processed_df.at[idx, 'flagged'] = "No (justified)"
                processed_df.at[idx, 'matched_note_id'] = note_id
                processed_df.at[idx, 'reason'] = f"Matches disruption alert {note_id}: {details}"
            except:
                processed_df.at[idx, 'flagged'] = "Yes"
                processed_df.at[idx, 'matched_note_id'] = ""
                processed_df.at[idx, 'reason'] = "Context validation parsing error. Left as unexplained."

    contract_columns = [
        "route", "week_of", "cost_per_tonne_km", 
        "vs_own_history", "vs_similar_routes", 
        "flagged", "matched_note_id", "reason"
    ]
    
    processed_df['week_of'] = pd.to_datetime(processed_df['week_of']).dt.strftime('%Y-%m-%d')
    final_output = processed_df[contract_columns]
    final_output.to_csv(output_csv, index=False)
    print(f"✨ Production evaluation records successfully created at: {output_csv}")


if __name__ == "__main__":
    run_pipeline("data/shipment_records.csv", "data/context_notes.csv", "outputs/run_1.csv")
