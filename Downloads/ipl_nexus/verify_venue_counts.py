import pandas as pd
import json

# Load raw data
df = pd.read_csv('data/IPL_matches.csv')

# Check high-scoring venues (avg >= 190)
print("=== VERIFYING HIGH-SCORING VENUES (Avg >= 190) ===\n")

venues_to_check = [
    "Himachal Pradesh Cricket Association Stadium, Dharamsala",
    "Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh",
    "Maharaja Yadavindra Singh International Cricket Stadium, New Chandigarh"
]

for venue in venues_to_check:
    venue_matches = df[df['venue'] == venue]
    
    if len(venue_matches) > 0:
        avg_score = venue_matches['first_innings_runs'].mean()
        print(f"\n{venue}")
        print(f"  Total matches: {len(venue_matches)}")
        print(f"  Avg first innings: {avg_score:.1f}")
        print(f"  Seasons: {sorted(venue_matches['season'].dropna().unique().tolist())}")
    else:
        print(f"\n{venue} - NOT FOUND, checking similar names")
        similar = df[df['venue'].str.contains('Himachal' if 'Himachal' in venue else 'Punjab' if 'Punjab' in venue else 'Maharaja', na=False)]['venue'].unique()
        print(f"  Similar venues found: {list(similar)}")

# Also check all venues with high average scores
print("\n\n=== ALL VENUES WITH AVG >= 190 ===\n")
venue_stats = df.groupby('venue').agg({
    'first_innings_runs': 'mean',
    'match_id': 'count'
}).reset_index()
venue_stats.columns = ['venue', 'avg_score', 'total_matches']
high_scoring = venue_stats[venue_stats['avg_score'] >= 190].sort_values('avg_score', ascending=False)

for _, row in high_scoring.iterrows():
    print(f"{row['venue']}: {row['total_matches']} matches, avg {row['avg_score']:.1f}")
