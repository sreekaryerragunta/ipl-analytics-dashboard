import json

data = json.load(open('webapp/static/data/player_matchup_data.json'))

# Check for MS Dhoni vs SL Malinga
key = 'MS_Dhoni_vs_SL_Malinga'
exists = key in data['matchups']
print(f'MS Dhoni vs SL Malinga exists: {exists}')

if exists:
    matchup = data['matchups'][key]
    print(f"\nOverall: {matchup['overall'] is not None}")
    print(f"Last 5: {matchup['last_5'] is not None}")
    print(f"Last 3: {matchup['last_3'] is not None}")
    
    if matchup['overall']:
        print(f"\nOverall stats: {matchup['overall']['balls']} balls, {matchup['overall']['runs']} runs")
    
    if matchup['season_wise']:
        print(f"\nSeasons available: {list(matchup['season_wise'].keys())}")
else:
    # Try to find the correct key
    dhoni_keys = [k for k in data['matchups'].keys() if 'Dhoni' in k and 'Malinga' in k]
    print(f"Found Dhoni-Malinga keys: {dhoni_keys}")
