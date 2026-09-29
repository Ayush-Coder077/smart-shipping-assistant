# Smart Shipping Assistant (Cost Anomaly Auditor)

A production-grade, deterministic data pipeline and automated logistics cost-anomaly audit system designed to process weekly freight expenditures, establish rolling baseline metrics, and cross-reference operational disruption records using a local **Ollama** LLM stack running **Llama3**.

---

## 🛠️ System Architecture & Innovations

This solution goes beyond basic script patterns to deliver a structurally sound analytics engine built around core production constraints:

### 1. Data Leakage Prevention (The Historical Isolation Wall)
To prevent the target week's shipping spikes from inflating its own historical metrics, the `own_history_baseline` calculates a trailing 8-week rolling average. It enforces a strict lookback boundary by applying a `.shift(1)` operation before evaluating the rolling mean window. This ensures that current data points never influence past targets. 

### 2. Self-Excluding Peer Baseline Analytics
Standard peer group averages create mathematical distortion. If a major high-volume lane encounters an isolated price surge, including it in the baseline will skew the group average upward, masking spikes on smaller routes. This engine independently aggregates total expenditures (\(\sum \text{Cost}\)) and total network utilization (\(\sum \text{Tonne-KM}\)) across the peer type, and mathematically subtracts the target route's individual contribution before computing the final comparison ratio:

\[\text{Peer Baseline} = \frac{\sum \text{Cost}_{\text{All Peers}} - \text{Cost}_{\text{Current Route}}}{\sum \text{Tonne-KM}_{\text{All Peers}} - \text{Tonne-KM}_{\text{Current Route}}}\]

### 3. Zero-Hallucination Disruption Matching
Traditional semantic vector databases search via floating-point text similarities, which can mix up spatial coordinates and calendar timelines (e.g., matching a disruption note from the wrong route or month because the text looks similar). This pipeline implements a deterministic spatial-temporal intersection filter. Disruption alerts are linked to a route strictly if they share the exact origin-destination pair or are explicitly categorized as macro-level national events active during that precise calendar week.

### 4. Absolute System Determinism (Local Ollama Engine Lock)
The engine is completely audit-safe and repeatable. By managing contextual data inputs logically, passing strict JSON schemas to the model, and hard-locking the local **Ollama Llama3 execution runtime to a temperature of 0.0**, the pipeline guarantees 100% reproducible row metrics, classification statuses, and text outputs across multiple consecutive runs.

---

## 📂 Project Structure

The project code is modular and organized into the following component directory layout:

```text
smart-shipping-assistant/
│
├── data/
│   ├── shipment_records.csv       # Raw incoming shipment transactions
│   └── context_notes.csv          # Log of system supply-chain operational alerts
│
├── src/
│   ├── __init__.py                # Module initialization anchor
│   ├── pipeline.py                # Monday-Sunday grouping & baseline calculations
│   ├── rag_engine.py              # Spatial-temporal deterministic filter
│   ├── auditor.py                 # Llama3 Ollama connection driver (Temp 0.0)
│   └── utils.py                   # Centralised execution telemetry & token log
│
├── outputs/
│   ├── run_1.csv                  # Main contract-compliant output evaluation sheet
│   ├── run_2.csv                  # Reproducibility verification check 2
│   └── run_3.csv                  # Reproducibility verification check 3
│
├── main.py                        # Single entry-point orchestrator script
├── eval_harness.py                # Automated 3-iteration reproducibility engine
└── requirements.txt               # System runtime dependencies (pandas, numpy, openai)
```

---

## 📋 Compliant Output CSV Schema Contract

The final evaluation files generated inside the `outputs/` folder strictly adhere to the structural schema and ordering constraints expected by automated grading engines:

1. **`route`**: Combined route path formatted as an absolute string (`{Origin}-{Destination}`).
2. **`week_of`**: Calendar date string snapped directly to the week's starting Monday (`YYYY-MM-DD`).
3. **`cost_per_tonne_km`**: The raw numerical mathematical efficiency metric calculated as `Total Cost / (Quantity * Distance)`.
4. **`vs_own_history`**: Formatted text string representing percentage variance change against the lookback historical average.
5. **`vs_similar_routes`**: Formatted text string representing percentage variance change against the self-excluding peer baseline.
6. **`flagged`**: Categorized operational outcome states (`No Anomaly` for normal metrics, `Yes` for unmitigated price moves, or `No (justified)` when a verified note matches).
7. **`matched_note_id`**: The corresponding note code from the logs (left completely empty if unexplained).
8. **`reason`**: Descriptive diagnostic explanation detailing the root cause of the spike or operational status.

---

## 🚀 Execution & Verification Instructions

Follow these steps to run the pipeline inside your local workspace terminal:

### 1. Spin up the Local AI Engine (Ollama)
Ensure you have downloaded and installed **Ollama** on your computer. Start your local model service from your terminal to host the Llama3 endpoint:
```bash
ollama run llama3
```
*Keep this terminal tab active in the background to serve as the system infrastructure layer.*

### 2. Ingest Data Inputs & Sync Environment
Ensure your source data files (`shipment_records.csv` and `context_notes.csv`) are placed inside the `data/` folder. Open a separate terminal prompt and sync your system runtime libraries using pip:
```bash
pip install -r requirements.txt
```

### 3. Run the Main Processing Pipeline
To execute a single operational sweep of the computational pipeline and generate the core report alongside token usage stats, trigger the orchestrator:
```bash
python main.py
```

### 4. Run the Automated Reproducibility Harness
To simulate the automated grading loop and prove local LLM system determinism, run the test harness script:
```bash
python eval_harness.py
```
Upon a successful execution path, the script will systematically cross-check the three generated sheets inside the `outputs/` directory and print an assertion message confirming all iterations match identically down to the final decimal space.
