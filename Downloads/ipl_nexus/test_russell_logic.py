import pandas as pd

def calculate_stats(balls_df):
    """Calculate H2H stats from filtered balls (Optimized logic)"""
    if len(balls_df) == 0:
        return None
    
    # Filter out wides for ball counts and batting stats
    if 'extra_type' in balls_df.columns:
        valid_balls_df = balls_df[balls_df['extra_type'] != 'wides']
    else:
        valid_balls_df = balls_df

    total_balls = len(valid_balls_df)
    total_runs = balls_df['runs_batter'].sum() if 'runs_batter' in balls_df.columns else 0
    
    # Dismissals (use ALL balls)
    dismissals = 0
    if 'wicket_kind' in balls_df.columns:
        dismissals = len(balls_df[
            (balls_df['wicket_kind'].notna()) & 
            (~balls_df['wicket_kind'].str.contains('run out', case=False, na=False))
        ])
    
    avg = round(total_runs / dismissals, 2) if dismissals > 0 else total_runs
    sr = round((total_runs / total_balls) * 100, 2) if total_balls > 0 else 0
    
    return {
        "balls": int(total_balls),
        "runs": int(total_runs),
        "dismissals": int(dismissals),
        "avg": float(avg),
        "sr": float(sr)
    }

print("TESTING LOGIC: AD Russell vs Mohammed Siraj")
df = pd.read_csv('data/IPL.csv', low_memory=False)
mask = (df['batter'] == 'AD Russell') & (df['bowler'] == 'Mohammed Siraj')
matchup_df = df[mask].copy()

print(f"Total rows: {len(matchup_df)}")

stats = calculate_stats(matchup_df)
print("\nGenerated Stats:")
print(stats)

if stats['balls'] == 20 and stats['runs'] == 23 and abs(stats['sr'] - 115.0) < 0.1:
    print("\nSUCCESS: Logic produced expected results!")
else:
    print("\nFAILURE: Logic produced unexpected results.")
