import json

data = json.load(open('webapp/static/data/player_matchup_data.json'))
print(f'Total matchups: {len(data["matchups"])}')

# Check for A Mhatre vs JJ Bumrah
key = 'A_Mhatre_vs_JJ_Bumrah'
exists = key in data['matchups']
print(f'A Mhatre vs JJ Bumrah exists: {exists}')

# Check if A Mhatre is in batsmen list
a_mhatre_in_batsmen = 'A Mhatre' in data['batsmen']
print(f'A Mhatre in batsmen list: {a_mhatre_in_batsmen}')

# Find all Mhatre variants
mhatre_variants = [b for b in data['batsmen'] if 'Mhatre' in b]
print(f'Mhatre variants in data: {mhatre_variants}')

# Check JJ Bumrah
jj_bumrah_in_bowlers = 'JJ Bumrah' in data['bowlers']
print(f'JJ Bumrah in bowlers list: {jj_bumrah_in_bowlers}')
