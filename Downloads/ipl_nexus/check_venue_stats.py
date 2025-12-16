import pandas as pd

df = pd.read_csv('data/IPL_matches.csv')

venues = df.groupby('venue').agg({
    'match_id': 'count',
    'first_innings_runs': 'mean'
}).reset_index()

venues.columns = ['Venue', 'Matches', 'Avg_Score']
venues = venues.sort_values('Avg_Score', ascending=False)

print('=== TOP 20 VENUES BY AVERAGE SCORE ===\n')
print(venues.head(20).to_string(index=False))

print(f'\n\nVenues with avg >= 190: {len(venues[venues["Avg_Score"] >= 190])}')
print(f'Venues with avg >= 180: {len(venues[venues["Avg_Score"] >= 180])}')
print(f'Venues with avg >= 175: {len(venues[venues["Avg_Score"] >= 175])}')
print(f'Venues with avg >= 170: {len(venues[venues["Avg_Score"] >= 170])}')
print(f'Venues with avg >= 165: {len(venues[venues["Avg_Score"] >= 165])}')
