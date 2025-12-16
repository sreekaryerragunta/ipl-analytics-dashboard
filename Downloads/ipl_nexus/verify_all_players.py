import pandas as pd
import json

print("=" * 80)
print("COMPREHENSIVE PLAYER MATCHUP VERIFICATION")
print("=" * 80)

# Load the source data
print("\n1. Loading source data (IPL.csv)...")
df = pd.read_csv('data/IPL.csv', low_memory=False)
print(f"   Total balls in dataset: {len(df):,}")

# Get unique players from source
unique_batsmen_source = set(df['batter'].dropna().unique())
unique_bowlers_source = set(df['bowler'].dropna().unique())
print(f"   Unique batsmen in source: {len(unique_batsmen_source)}")
print(f"   Unique bowlers in source: {len(unique_bowlers_source)}")

# Load the generated matchup data
print("\n2. Loading generated matchup data...")
with open('webapp/static/data/player_matchup_data.json', 'r') as f:
    matchup_data = json.load(f)

batsmen_in_json = set(matchup_data['batsmen'])
bowlers_in_json = set(matchup_data['bowlers'])
print(f"   Batsmen in JSON: {len(batsmen_in_json)}")
print(f"   Bowlers in JSON: {len(bowlers_in_json)}")
print(f"   Total matchups: {len(matchup_data['matchups']):,}")

# Check coverage
print("\n3. Checking coverage...")
missing_batsmen = unique_batsmen_source - batsmen_in_json
missing_bowlers = unique_bowlers_source - bowlers_in_json

print(f"   Missing batsmen: {len(missing_batsmen)}")
print(f"   Missing bowlers: {len(missing_bowlers)}")

if missing_batsmen:
    print(f"\n   First 20 missing batsmen: {sorted(list(missing_batsmen))[:20]}")
if missing_bowlers:
    print(f"\n   First 20 missing bowlers: {sorted(list(missing_bowlers))[:20]}")

# Check why they're missing - do they have any valid matchups?
print("\n4. Analyzing missing players...")
if missing_batsmen:
    sample_batsman = list(missing_batsmen)[0]
    sample_balls = df[df['batter'] == sample_batsman]
    print(f"\n   Sample missing batsman: {sample_batsman}")
    print(f"   Total balls faced: {len(sample_balls)}")
    
    # Check matchups
    matchups = sample_balls.groupby('bowler').size()
    matchups_6plus = matchups[matchups >= 6]
    print(f"   Matchups with 6+ balls: {len(matchups_6plus)}")
    if len(matchups_6plus) > 0:
        print(f"   Example matchups: {dict(list(matchups_6plus.items())[:3])}")

# Coverage verification
print("\n5. Coverage verification:")
print(f"   All batsmen included: {len(missing_batsmen) == 0}")
print(f"   All bowlers included: {len(missing_bowlers) == 0}")

# Check matchup generation logic
print("\n6. Checking matchup generation threshold...")
grouped = df.groupby(['batter', 'bowler']).size()
valid_pairs_6plus = grouped[grouped >= 6]
print(f"   Valid pairs (6+ balls): {len(valid_pairs_6plus):,}")
print(f"   Matchups in JSON: {len(matchup_data['matchups']):,}")
print(f"   Match: {len(valid_pairs_6plus) == len(matchup_data['matchups'])}")

# Sample verification - check specific players
print("\n7. Sample player verification:")
test_players = ['V Kohli', 'MS Dhoni', 'RG Sharma', 'A Mhatre', 'JJ Bumrah', 'SL Malinga']
for player in test_players:
    in_batsmen = player in batsmen_in_json
    in_bowlers = player in bowlers_in_json
    print(f"   {player:20s} - Batsman: {str(in_batsmen):5s} | Bowler: {str(in_bowlers):5s}")

# Check file size
import os
file_size = os.path.getsize('webapp/static/data/player_matchup_data.json')
print(f"\n8. File information:")
print(f"   File size: {file_size / (1024*1024):.2f} MB")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
