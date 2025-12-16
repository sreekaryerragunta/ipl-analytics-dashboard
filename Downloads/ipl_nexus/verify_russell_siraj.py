import pandas as pd
import json

print("=" * 80)
print("VERIFYING: AD Russell vs Mohammed Siraj")
print("=" * 80)

# 1. Check Source Data
print("\n1. Analyzing source data (IPL.csv)...")
df = pd.read_csv('data/IPL.csv', low_memory=False)

# Filter for the specific matchup
mask = (df['batter'] == 'AD Russell') & (df['bowler'] == 'Mohammed Siraj')
matchup_df = df[mask].copy()

print(f"   Total source records found: {len(matchup_df)}")

if len(matchup_df) > 0:
    # Basic Stats Calculation
    balls_faced = len(matchup_df)
    # Exclude wides for balls count (usually standard practice, but let's see how script does it)
    # The script uses len(matchup_df) which implies all rows are balls. 
    # Standard cricket stats: balls = legal deliveries. Wides are not balls faced.
    # Check 'extras_type' column if it exists or 'wides'
    
    # Let's approximate first
    total_runs = matchup_df['runs_batter'].sum()
    # Calculate stats using available columns
    balls_faced = len(matchup_df)
    total_runs = matchup_df['runs_batter'].sum()
    
    # Check for wides and adjust ball count
    wides_count = 0
    if 'extra_type' in matchup_df.columns:
        wides_count = len(matchup_df[matchup_df['extra_type'] == 'wides'])
        legal_balls = balls_faced - wides_count
        print(f"\n   --- Source Calculation ---")
        print(f"   Total Rows: {balls_faced}")
        print(f"   Wides Found: {wides_count}")
        print(f"   Legal Balls Faced: {legal_balls} (Expected in JSON)")
    else:
        print("\n   --- Source Calculation ---")
        print(f"   Balls (Rows): {balls_faced}")
    
    # Check if 'wicket_kind' exists for dismissals
    if 'wicket_kind' in matchup_df.columns:
        # Dismissals: any non-null wicket_kind implies a wicket, but we need to check if it's the batter
        # Usually checking wicket_kind is not NaN is sufficient for this matchup dataframe filtered by batter/bowler
        # However, run outs might attribute to non-striker.
        # Let's count all valid dismissals first
        valid_dismissals = matchup_df['wicket_kind'].notna()
        # Exclude 'retired hurt' etc if any
        dismissals_count = valid_dismissals.sum()
        
        print(f"   Runs (Batter): {total_runs}")
        print(f"   Dismissals (wicket_kind not null): {dismissals_count}")
        
        if legal_balls > 0:
            sr = (total_runs / legal_balls) * 100
            print(f"   Expected SR: {sr:.2f}")
        
        # Breakdown
        print(matchup_df[valid_dismissals][['season', 'match_id', 'innings', 'ball', 'runs_batter', 'wicket_kind']].to_string())
    else:
        print("   'wicket_kind' column missing.")

    print("\n   --- Ball-by-Ball Dump (First 10) ---")
    cols = [c for c in ['season', 'match_id', 'innings', 'ball', 'runs_batter', 'wicket_kind'] if c in matchup_df.columns]
    print(matchup_df[cols].head(10).to_string())

# 2. Check Generated JSON
print("\n\n2. Checking generated JSON...")
try:
    with open('webapp/static/data/player_matchup_data.json', 'r') as f:
        data = json.load(f)
        
    key = "AD_Russell_vs_Mohammed_Siraj"
    if key in data['matchups']:
        m = data['matchups'][key]['overall']
        print(f"   JSON Stats: {m}")
    else:
        print("   Matchup not found in JSON keys.")
except Exception as e:
    print(f"   Error reading JSON: {e}")
