import json

data = json.load(open('webapp/static/data/player_matchup_data.json'))
key = 'V_Kohli_vs_JJ_Bumrah'
exists = key in data['matchups']
print(f'V Kohli vs JJ Bumrah exists: {exists}')
if exists:
    m = data['matchups'][key]
    print(f"\nOverall Stats:")
    print(f"  Balls: {m['overall']['balls']}")
    print(f"  Runs: {m['overall']['runs']}")
    print(f"  Dismissals: {m['overall']['dismissals']}")
    print(f"  Average: {m['overall']['avg']}")
    print(f"  Strike Rate: {m['overall']['sr']}")
    print(f"  Dot %: {m['overall']['dot_pct']}")
