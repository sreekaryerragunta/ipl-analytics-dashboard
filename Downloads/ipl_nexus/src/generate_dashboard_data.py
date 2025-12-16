import pandas as pd
import numpy as np
import json
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Ensure output directory exists
os.makedirs('webapp/static/data', exist_ok=True)

def load_matches():
    path = 'data/IPL_matches.csv'
    if not os.path.exists(path):
        print(f"Matches not found at {path}, please run process_data.py first.")
        # Attempt to run process_data if needed? 
        # For now assume it exists as per previous steps.
        return None
    return pd.read_csv(path)

def generate_elo_data(df):
    print("Generating Elo Data...")
    # Simple Elo implementation for export
    teams = set(df['team1'].dropna()).union(set(df['team2'].dropna()))
    ratings = {t: 1500 for t in teams}
    history = []
    
    k = 30
    df_sorted = df.sort_values('date')
    
    for idx, row in df_sorted.iterrows():
        t1, t2 = row['team1'], row['team2']
        winner = row['match_won_by']
        
        if pd.isna(t1) or pd.isna(t2): continue
        
        r1 = ratings.get(t1, 1500)
        r2 = ratings.get(t2, 1500)
        
        # Win prob
        p1 = 1 / (1 + 10 ** ((r2 - r1) / 400))
        
        # Outcome
        if winner == t1: s1 = 1
        elif winner == t2: s1 = 0
        else: s1 = 0.5 # Tie
        
        # Update
        r1_new = r1 + k * (s1 - p1)
        r2_new = r2 + k * ((1 - s1) - (1 - p1))
        
        ratings[t1] = r1_new
        ratings[t2] = r2_new
        
        history.append({
            'date': str(row['date'])[:10],
            'season': int(row['season']) if pd.notna(row['season']) else 0,
            'team': t1,
            'rating': round(r1_new, 1)
        })
        history.append({
            'date': str(row['date'])[:10],
            'season': int(row['season']) if pd.notna(row['season']) else 0,
            'team': t2,
            'rating': round(r2_new, 1)
        })
        
    # Save current ratings
    with open('webapp/static/data/current_elo.json', 'w') as f:
        json.dump(ratings, f)
        
    # Save history (optimized structure for charts)
    # Group by team
    history_df = pd.DataFrame(history)
    chart_data = {}
    for team in history_df['team'].unique():
        team_data = history_df[history_df['team'] == team]
        chart_data[team] = {
            'dates': team_data['date'].tolist(),
            'ratings': team_data['rating'].tolist()
        }
    
    with open('webapp/static/data/elo_history.json', 'w') as f:
        json.dump(chart_data, f)
        
    return ratings

def generate_venue_stats(df):
    print("Generating Venue Stats...")
    # Avg score, toss win impact
    # df has 'first_innings_runs', 'venue', 'toss_winner', 'match_won_by'
    
    stats = []
    for venue, group in df.groupby('venue'):
        if len(group) < 5: continue # Skip rare venues
        
        avg_score = group['first_innings_runs'].mean()
        
        # Chasing wins: winner != team batting first
        # We assume team1 batted first? data doesn't explicitly say who batted first in match-level 
        # unless we check toss decision.
        # Logic: if toss_winner == bat => toss_winner is bat_first.
        # if toss_winner == field => toss_winner is bat_second.
        
        matches_with_decision = group.dropna(subset=['toss_decision', 'toss_winner', 'match_won_by'])
        toss_wins = 0
        bat_first_wins = 0
        total = len(matches_with_decision)
        
        for _, row in matches_with_decision.iterrows():
            if row['toss_winner'] == row['match_won_by']:
                toss_wins += 1
            
            # Did bat first win?
            # If toss=bat and toss_winner=winner => bat first won
            # If toss=field and toss_winner!=winner => bat first won (since toss winner fielded and lost)
            t_win = row['toss_winner']
            t_dec = row['toss_decision']
            winner = row['match_won_by']
            
            # Identify bat first team
            if t_dec == 'bat':
                bat_first_team = t_win
            else:
                bat_first_team = row['team1'] if row['team1'] != t_win else row['team2']
            
            if winner == bat_first_team:
                bat_first_wins += 1
                
        if total > 0:
            stats.append({
                'venue': venue,
                'matches': int(total),
                'avg_first_innings': round(avg_score),
                'toss_win_pct': round(toss_wins / total * 100, 1),
                'bat_first_win_pct': round(bat_first_wins / total * 100, 1)
            })
            
    with open('webapp/static/data/venue_stats.json', 'w') as f:
        json.dump(stats, f)

def generate_archetypes(df):
    print("Generating Archetypes...")
    # Features: runs, wickets, margin
    # Ensure no NaNs in features
    features = df[['first_innings_runs', 'second_innings_runs', 'win_by_runs', 'win_by_wickets']].fillna(0)
    
    # Normalize
    scaler = StandardScaler()
    X = scaler.fit_transform(features)
    
    # Cluster
    kmeans = KMeans(n_clusters=4, random_state=42)
    clusters = kmeans.fit_predict(X)
    
    df['cluster'] = clusters
    
    # Analyze and Name Clusters
    cluster_stats = []
    for c in range(4):
        subset = df[df['cluster'] == c]
        avg_r1 = subset['first_innings_runs'].mean()
        avg_r2 = subset['second_innings_runs'].mean()
        avg_margin_runs = subset['win_by_runs'].mean()
        
        cluster_stats.append({
            'id': c,
            'avg_r1': avg_r1,
            'avg_r2': avg_r2,
            'avg_margin': avg_margin_runs,
            'count': len(subset)
        })
    
    # Dynamic Naming Heuristic
    # Sort by Total Match Runs (Avg R1 + Avg R2)
    cluster_stats.sort(key=lambda x: x['avg_r1'] + x['avg_r2'])
    
    # Assign names based on sorted characteristics
    # Lowest scores -> Defensive
    # Highest scores -> High Scoring
    # Middle ones -> check margins
    
    # Map old IDs to new Names/Metadata
    meta = {}
    
    # Identify the specific nature of each cluster
    # We can't guarantee order effectively without complex logic, so let's use thresholds
    
    for stat in cluster_stats:
        c_id = stat['id']
        total_runs = stat['avg_r1'] + stat['avg_r2']
        margin = stat['avg_margin']
        
        if total_runs > 350:
            name = "High Scoring Thrillers"
            desc = "Batting paradises with big totals and aggressive chases"
        elif total_runs < 280:
            name = "Defensive Battles"
            desc = "Low scoring matches dominated by bowlers"
        elif margin > 30: # Large run margin
            name = "One-Sided Dominance"
            desc = "Matches won by a substantial margin"
        else:
            name = "Competitive Chases"
            desc = "Balanced contests often decided in the final overs"
            
        meta[c_id] = {
            'name': name,
            'description': desc,
            'count': stat['count'],
            'avg_runs_1': round(stat['avg_r1']),
            'avg_runs_2': round(stat['avg_r2']),
            'avg_margin': round(stat['avg_margin'], 1)
        }

    print("Cluster Metadata:", meta)

    # Prepare Match List Export
    matches_export = []
    for idx, row in df.iterrows():
        # Determine readable result
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
    
    # Output Structure
    output_data = {
        'meta': meta,
        'matches': matches_export
    }
    
    output_file = 'webapp/static/data/archetypes.json'
    with open(output_file, 'w') as f:
        # ignore_nan=True is not standard in json.dump, we must fix headers.
        # But we handled checks above. default=str fallsafe just in case
        json.dump(output_data, f, indent=2)
    print(f"Saved archetype data with {len(matches_export)} matches to {output_file}")

def train_prediction_model(df):
    print("Training Prediction Model...")
    # Train a simple model to export feature importances or use for live predict via API
    # For now, we'll just save a dummy "win probability" matrix for the demo
    # or a small JSON of team-vs-team win rates to serve as "predictions"
    
    # Let's simple create a "Head to Head" matrix
    teams = df['team1'].dropna().unique()
    matrix = {}
    
    for t1 in teams:
        matrix[t1] = {}
        for t2 in teams:
            if t1 == t2: continue
            
            # Find matches
            mask = ((df['team1'] == t1) & (df['team2'] == t2)) | ((df['team1'] == t2) & (df['team2'] == t1))
            matches = df[mask]
            
            if len(matches) == 0:
                prob = 0.5
            else:
                wins = len(matches[matches['match_won_by'] == t1])
                prob = wins / len(matches)
                # Weighted by recent form? simplified for now.
            
            matrix[t1][t2] = round(prob, 2)
            
    with open('webapp/static/data/h2h_matrix.json', 'w') as f:
        json.dump(matrix, f)

def main():
    df = load_matches()
    if df is None: return
    
    generate_elo_data(df)
    generate_venue_stats(df)
    generate_archetypes(df)
    train_prediction_model(df)
    print("Dashboard data generated successfully.")

if __name__ == "__main__":
    main()
