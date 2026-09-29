import pandas as pd
import numpy as np

def calculate_baselines(shipment_path: str) -> pd.DataFrame:
    df = pd.read_csv(shipment_path)
    
    df.columns = df.columns.str.strip().str.lower()
    
  
    qty_col = next((c for c in df.columns if 'quantity' in c or 'qty' in c or 'weight' in c), None)
    dist_col = next((c for c in df.columns if 'distance' in c or 'km' in c), None)
    date_col = next((c for c in df.columns if 'date' in c or 'time' in c), None)
    cost_col = next((c for c in df.columns if 'cost' in c or 'price' in c or 'freight' in c), None)
    
    missing = []
    if not qty_col: missing.append("quantity")
    if not dist_col: missing.append("distance")
    if not date_col: missing.append("shipment_date")
    if not cost_col: missing.append("cost")
    
    if missing:
        raise KeyError(f"❌ Critical columns missing in CSV: {missing}. Available columns are: {list(df.columns)}")

    df['shipment_date'] = pd.to_datetime(df[date_col])
    
    df['week_of'] = df['shipment_date'].dt.to_period('W-SUN').dt.start_time
    df['tonne_km'] = df[qty_col] * df[dist_col]
    
    origin_col = next((c for c in df.columns if 'origin' in c or 'source' in c or 'from' in c), 'origin')
    dest_col = next((c for c in df.columns if 'dest' in c or 'to' in c), 'destination')
    type_col = next((c for c in df.columns if 'type' in c or 'length' in c), 'route_type')

    route_weekly = df.groupby([origin_col, dest_col, type_col, 'week_of']).agg(
        total_cost=(cost_col, 'sum'),
        total_tonne_km=('tonne_km', 'sum')
    ).reset_index()
    
    route_weekly['cost_per_tonne_km'] = route_weekly['total_cost'] / route_weekly['total_tonne_km']
    route_weekly = route_weekly.sort_values(by=[origin_col, dest_col, 'week_of']).reset_index(drop=True)
    
    route_weekly['own_history_val'] = route_weekly.groupby([origin_col, dest_col])['cost_per_tonne_km'].transform(
        lambda x: x.shift(1).rolling(window=8, min_periods=1).mean()
    )
    
    peer_stats = route_weekly.groupby([type_col, 'week_of']).agg(
        peer_sum_cost=('total_cost', 'sum'),
        peer_sum_tonne_km=('total_tonne_km', 'sum')
    ).reset_index()
    
    route_weekly = route_weekly.merge(peer_stats, on=[type_col, 'week_of'], how='left')
    
    route_weekly['peer_val'] = (
        (route_weekly['peer_sum_cost'] - route_weekly['total_cost']) / 
        (route_weekly['peer_sum_tonne_km'] - route_weekly['total_tonne_km'])
    )
    
    route_weekly['route'] = route_weekly[origin_col].astype(str) + '-' + route_weekly[dest_col].astype(str)
    
    pct_hist = ((route_weekly['cost_per_tonne_km'] - route_weekly['own_history_val']) / route_weekly['own_history_val']) * 100
    pct_peer = ((route_weekly['cost_per_tonne_km'] - route_weekly['peer_val']) / route_weekly['peer_val']) * 100
    
    route_weekly['vs_own_history'] = pct_hist.apply(lambda x: f"+{x:.1f}% vs this route's past average" if x >= 0 else f"{x:.1f}% vs this route's past average")
    route_weekly['vs_similar_routes'] = pct_peer.apply(lambda x: f"+{x:.1f}% vs similar-length routes this week" if x >= 0 else f"{x:.1f}% vs similar-length routes this week")
    
    route_weekly['is_anomaly'] = (route_weekly['cost_per_tonne_km'] > route_weekly['own_history_val']) & \
                                 (route_weekly['cost_per_tonne_km'] > route_weekly['peer_val'])
                                 
    return route_weekly
