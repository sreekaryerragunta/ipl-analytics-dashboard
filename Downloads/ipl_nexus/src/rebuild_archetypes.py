import pandas as pd
import json
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

print("Loading matches data...")
df = pd.read_csv('data/IPL_matches.csv')

print(f"Total matches: {len(df)}")

# Prepare features for clustering
features = df[['first_innings_runs', 'second_innings_runs', 'win_by_runs', 'win_by_wickets']].fillna(0)

# Normalize
scaler = StandardScaler()
X = scaler.fit_transform(features)

# Cluster
print("\nPerforming KMeans clustering...")
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
clusters = kmeans.fit_predict(X)

df['cluster'] = clusters

# Analyze each cluster to assign UNIQUE names
print("\nAnalyzing clusters...")
cluster_analysis = []
for c in range(4):
    subset = df[df['cluster'] == c]
    
    analysis = {
        'id': c,
        'count': len(subset),
        'avg_r1': subset['first_innings_runs'].mean(),
        'avg_r2': subset['second_innings_runs'].mean(),
        'avg_total': subset['first_innings_runs'].mean() + subset['second_innings_runs'].mean(),
        'avg_margin_runs': subset['win_by_runs'].mean(),
        'avg_margin_wkts': subset['win_by_wickets'].mean(),
        'close_games': len(subset[(subset['win_by_runs'] < 10) | (subset['win_by_wickets'] < 3)]) / len(subset) * 100
    }
    cluster_analysis.append(analysis)
    
    print(f"\nCluster {c}:")
    print(f"  Matches: {analysis['count']}")
    print(f"  Avg 1st Inn: {analysis['avg_r1']:.1f}")
    print(f"  Avg 2nd Inn: {analysis['avg_r2']:.1f}")
    print(f"  Avg Total: {analysis['avg_total']:.1f}")
    print(f"  Avg Run Margin: {analysis['avg_margin_runs']:.1f}")
    print(f"  Close Games %: {analysis['close_games']:.1f}%")

# Assign UNIQUE names based on comprehensive characteristics
# First, sort clusters by total runs to understand the spectrum
sorted_by_runs = sorted(cluster_analysis, key=lambda x: x['avg_total'], reverse=True)

# Create a mapping of characteristics
cluster_chars = {}
for analysis in cluster_analysis:
    c_id = analysis['id']
    cluster_chars[c_id] = {
        'total_runs': analysis['avg_total'],
        'margin': analysis['avg_margin_runs'],
        'r1': analysis['avg_r1'],
        'r2': analysis['avg_r2'],
        'close_pct': analysis['close_games']
    }

meta = {}

# Assign names based on unique position in the spectrum
for analysis in cluster_analysis:
    c_id = analysis['id']
    chars = cluster_chars[c_id]
    
    # Cluster 1: Highest total runs (349) - High Scoring
    if chars['total_runs'] > 348:
        name = "High Scoring Thrillers"
        desc = "Batting paradises with big totals and aggressive chases"
    
    # Cluster 3: High runs (344) but balanced (both innings ~170) - Competitive
    elif chars['total_runs'] > 340 and abs(chars['r1'] - chars['r2']) < 10:
        name = "Balanced Shootouts"
        desc = "Evenly matched high-scoring contests"
    
    # Cluster 2: Moderate runs (317) but high margin (69.5) - One-sided
    elif chars['margin'] > 50:
        name = "One-Sided Dominance"
        desc = "Matches won by substantial margins"
    
    # Cluster 0: Lowest runs (242) - Low Scoring
    elif chars['total_runs'] < 280:
        name = "Defensive Battles"
        desc = "Low scoring matches dominated by bowlers"
    
    # Fallback
    else:
        name = f"Cluster {c_id} Pattern"
        desc = "Unique match characteristics"
    
    meta[c_id] = {
        'name': name,
        'description': desc,
        'count': analysis['count'],
        'avg_runs_1': round(analysis['avg_r1']),
        'avg_runs_2': round(analysis['avg_r2']),
        'avg_margin': round(analysis['avg_margin_runs'], 1)
    }

print("\n\nFinal Cluster Names:")
for c_id, m in meta.items():
    print(f"Cluster {c_id}: {m['name']} ({m['count']} matches)")

# Check for duplicates
names = [m['name'] for m in meta.values()]
if len(names) != len(set(names)):
    print("\nWARNING: Duplicate names detected!")
    print("Names:", names)
else:
    print("\nAll cluster names are unique!")

# Prepare match export
matches_export = []
for idx, row in df.iterrows():
    if row['win_by_runs'] > 0:
        margin = f"{int(row['win_by_runs'])} runs"
    elif row['win_by_wickets'] > 0:
        margin = f"{int(row['win_by_wickets'])} wkts"
    else:
        margin = "Tie/NR"
        
    matches_export.append({
        'id': str(row['match_id']),
        'season': int(row['season']) if pd.notna(row['season']) else 0,
        'date': str(row['date']) if pd.notna(row['date']) else "",
        'team1': row['team1'] if pd.notna(row['team1']) else "Unknown",
        'team2': row['team2'] if pd.notna(row['team2']) else "Unknown",
        'winner': row['match_won_by'] if pd.notna(row['match_won_by']) else "No Result",
        'venue': row['venue'] if pd.notna(row['venue']) else "Unknown Venue",
        'toss_winner': row['toss_winner'] if pd.notna(row['toss_winner']) else "",
        'toss_decision': row['toss_decision'] if pd.notna(row['toss_decision']) else "",
        'score1': int(row['first_innings_runs']) if pd.notna(row['first_innings_runs']) else 0,
        'score2': int(row['second_innings_runs']) if pd.notna(row['second_innings_runs']) else 0,
        'margin': margin,
        'cluster': int(row['cluster'])
    })

# Save
output = {
    'meta': meta,
    'matches': matches_export
}

output_file = 'webapp/static/data/archetypes.json'
with open(output_file, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nSaved {len(matches_export)} matches to {output_file}")
