import pandas as pd

df = pd.read_csv('data/IPL_matches.csv')

# Check RCB at Narendra Modi Stadium in 2024
rcb_2024 = df[
    (df['season'] == 2024) & 
    ((df['team1'] == 'Royal Challengers Bengaluru') | (df['team2'] == 'Royal Challengers Bengaluru')) & 
    (df['venue'] == 'Narendra Modi Stadium')
]

print(f'RCB matches at Narendra Modi Stadium in 2024: {len(rcb_2024)}')
print('\nMatch details:')
for _, m in rcb_2024.iterrows():
    print(f"  {m['date']}: {m['team1']} vs {m['team2']} - Winner: {m['match_won_by']}")

# Also check all-time
rcb_all_time = df[
    ((df['team1'] == 'Royal Challengers Bengaluru') | (df['team2'] == 'Royal Challengers Bengaluru')) & 
    (df['venue'] == 'Narendra Modi Stadium')
]
print(f'\nRCB matches at Narendra Modi Stadium ALL TIME: {len(rcb_all_time)}')
print('Seasons:', sorted(rcb_all_time['season'].dropna().unique().tolist()))
