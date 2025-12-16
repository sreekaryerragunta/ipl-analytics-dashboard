import pandas as pd

print("VERIFYING WIDES: AD Russell vs Mohammed Siraj")
df = pd.read_csv('data/IPL.csv', low_memory=False)
mask = (df['batter'] == 'AD Russell') & (df['bowler'] == 'Mohammed Siraj')
matchup_df = df[mask].copy()

print("\nColumns available:", matchup_df.columns.tolist())

# Check for extras
if 'extra_type' in matchup_df.columns:
    print("\nRows with extra_type:")
    extras = matchup_df[matchup_df['extra_type'].notna()]
    print(extras[['season', 'ball', 'runs_batter', 'runs_extras', 'extra_type']].to_string())
else:
    print("No 'extra_type' column. Checking 'runs_extras' > 0")
    extras = matchup_df[matchup_df['runs_extras'] > 0]
    print(extras[['season', 'ball', 'runs_batter', 'runs_extras']].to_string())
