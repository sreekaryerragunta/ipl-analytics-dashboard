import pandas as pd
import json
import os
import numpy as np

def generate_prediction_data():
    print("Generating Advanced Prediction Data...")
    
    # Load matches
    try:
        df = pd.read_csv('data/IPL_matches.csv')
    except FileNotFoundError:
        print("Error: data/IPL_matches.csv not found.")
        return

    # Ensure output dir
    os.makedirs('webapp/static/data', exist_ok=True)

    # Get all teams
    teams = sorted(list(set(df['team1'].dropna()).union(set(df['team2'].dropna()))))
    
    current_year = pd.Timestamp.now().year
    # If using dataset that might be older, find max season
    if 'season' in df.columns:
        max_season = df['season'].max()
        current_year = int(max_season)

    prediction_data = {
        "teams": teams,
        "matchups": {}
    }

    def get_stats(matches, t1, t2):
        if len(matches) == 0:
            return None
        
        played = len(matches)
        
        # Wins
        t1_wins = len(matches[matches['match_won_by'] == t1])
        t2_wins = len(matches[matches['match_won_by'] == t2])
        draws = len(matches) - (t1_wins + t2_wins)
        
        t1_win_pct = round((t1_wins / played) * 100, 1)
        t2_win_pct = round((t2_wins / played) * 100, 1)

        # Avg Scores (approximate if only match aggregates available)
        # matches has team_runs if available, but let's filter specifically
        # We need to look at rows where t1 is batting first vs t2 batting first?
        # Dataset structure: 'first_innings_runs', 'team1', 'team2', 'toss_decision', 'toss_winner'
        
        # Simple avg score regardless of batting first/second for now, or refine?
        # Let's try to get score when batting.
        
        # T1 runs:
        # If t1 is team1 (bat first?) - checking dataset structure in mind
        # Usually 'first_innings_runs' corresponds to team batting first.
        # We need to know who batted first.
        
        t1_scores = []
        t2_scores = []
        
        for _, m in matches.iterrows():
            # Determine who batted first
            bat_first = None
            if m['toss_decision'] == 'bat':
                bat_first = m['toss_winner']
            else:
                bat_first = m['team1'] if m['toss_winner'] == m['team2'] else m['team2']
            
            if bat_first == t1:
                if pd.notna(m['first_innings_runs']): t1_scores.append(m['first_innings_runs'])
                if pd.notna(m['second_innings_runs']): t2_scores.append(m['second_innings_runs'])
            else:
                if pd.notna(m['first_innings_runs']): t2_scores.append(m['first_innings_runs'])
                if pd.notna(m['second_innings_runs']): t1_scores.append(m['second_innings_runs'])

        avg_t1 = int(np.mean(t1_scores)) if t1_scores else 0
        avg_t2 = int(np.mean(t2_scores)) if t2_scores else 0
        
        # Insights calculation
        insights = []
        
        # Dominance
        if t1_wins > t2_wins + played * 0.2: # Significant lead
            insights.append(f"{t1} has dominated this matchup recently.")
        elif t2_wins > t1_wins + played * 0.2:
            insights.append(f"{t2} has dominated this matchup recently.")
        elif abs(t1_wins - t2_wins) <= 1 and played > 2:
            insights.append("This is a closely contested rivalry.")
            
        # Batting First vs Chasing
        # Filter wins by t1
        t1_wins_rows = matches[matches['match_won_by'] == t1]
        t1_bat_first_wins = 0
        for _, m in t1_wins_rows.iterrows():
            bat_first = m['toss_winner'] if m['toss_decision'] == 'bat' else (m['team1'] if m['toss_winner'] == m['team2'] else m['team2'])
            if bat_first == t1:
                t1_bat_first_wins += 1
                
        t1_chase_wins = t1_wins - t1_bat_first_wins
        
        if t1_wins >= 2:
            if t1_chase_wins > t1_bat_first_wins:
                insights.append(f"{t1} prefers chasing against {t2} ({t1_chase_wins} wins chasing).")
            elif t1_bat_first_wins > t1_chase_wins:
                insights.append(f"{t1} defends well against {t2} ({t1_bat_first_wins} wins batting first).")
        
        return {
            "played": played,
            "t1_wins": t1_wins,
            "t2_wins": t2_wins,
            "draws": draws,
            "t1_win_pct": t1_win_pct,
            "t2_win_pct": t2_win_pct,
            "avg_score_t1": avg_t1,
            "avg_score_t2": avg_t2,
            "insights": insights
        }

    # Generate pairwise data
    for i, t1 in enumerate(teams):
        for j, t2 in enumerate(teams):
            if i >= j: continue # Avoid duplicates, but frontend needs t1_vs_t2 lookup. 
                                # Actually better to store both keys or canonical key?
                                # Storing canonical key "A_vs_B" where A < B alphabetically is efficient.
            
            # Canonical Key
            k1, k2 = sorted([t1, t2])
            key = f"{k1}_vs_{k2}"
            
            # Filter matches
            mask = ((df['team1'] == k1) & (df['team2'] == k2)) | ((df['team1'] == k2) & (df['team2'] == k1))
            pair_matches = df[mask]
            
            if len(pair_matches) == 0:
                continue

            # Timeframes
            # 1. Overall
            overall_stats = get_stats(pair_matches, k1, k2)
            
            # 2. Last 5 Seasons
            last_5 = pair_matches[pair_matches['season'] >= (current_year - 5)]
            l5_stats = get_stats(last_5, k1, k2)
            
            # 3. Last 3 Seasons
            last_3 = pair_matches[pair_matches['season'] >= (current_year - 3)]
            l3_stats = get_stats(last_3, k1, k2)
            
            # 4. Venue-wise Stats (Computed on Frontend now for dynamic filtering)
            # We skip backend pre-calculation to avoid sync issues with filters.

            # 5. Full Match List for Scorecards
            match_list = []
            # Sort by date desc
            pair_matches_sorted = pair_matches.sort_values('date', ascending=False)
            
            for _, m in pair_matches_sorted.iterrows():
                # Margin string logic
                margin = "Tie"
                if m.get('win_by_runs', 0) > 0:
                    margin = f"{int(m['win_by_runs'])} runs"
                elif m.get('win_by_wickets', 0) > 0:
                    margin = f"{int(m['win_by_wickets'])} wkts"
                
                match_list.append({
                    'id': int(m['match_id']) if pd.notna(m.get('match_id')) else 0,
                    'season': int(m['season']) if pd.notna(m.get('season')) else 0,
                    'date': str(m['date'])[:10] if pd.notna(m.get('date')) else "",
                    'venue': m.get('venue', ""),
                    'team1': m.get('team1', ""),
                    'team2': m.get('team2', ""),
                    'toss_winner': m.get('toss_winner', ""),
                    'toss_decision': m.get('toss_decision', ""),
                    'winner': m.get('match_won_by', ""),
                    'win_margin': margin,
                    'score1': int(m['first_innings_runs']) if pd.notna(m.get('first_innings_runs')) else 0,
                    'score2': int(m['second_innings_runs']) if pd.notna(m.get('second_innings_runs')) else 0,
                    'mom': "N/A" # Column missing in current dataset
                })

            prediction_data["matchups"][key] = {
                "overall": overall_stats,
                "last_5": l5_stats,
                "last_3": l3_stats,
                "matches": match_list
            }

    # Save
    with open('webapp/static/data/prediction_data.json', 'w') as f:
        json.dump(prediction_data, f, indent=2)
    
    print(f"Generated prediction data for {len(prediction_data['matchups'])} matchups.")

if __name__ == "__main__":
    generate_prediction_data()
