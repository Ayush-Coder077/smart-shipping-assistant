import pandas as pd
import numpy as np
from src.pipeline import calculate_baselines

def test_pipeline_math_logic(tmp_path):
    d = tmp_path / "mock_shipments.csv"
    mock_data = pd.DataFrame({
        'origin': ['A', 'A', 'A'],
        'destination': ['B', 'B', 'B'],
        'route_type': ['Short', 'Short', 'Short'],
        'shipment_date': ['2026-03-02', '2026-03-03', '2026-03-09'],
        'quantity':[],
        'distance':[],
        'cost': [1000, 1000, 1000]
    })
    mock_data.to_csv(d, index=False)
    
    res = calculate_baselines(str(d))
    
    assert len(res) == 2 
   
    assert res.loc[0, 'cost_per_tonne_km'] == 1.0
