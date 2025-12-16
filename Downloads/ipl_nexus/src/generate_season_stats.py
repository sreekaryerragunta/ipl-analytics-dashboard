import pandas as pd
import json
import os

def generate_season_stats():
    """Generate season-wise statistics for overview charts"""
    
    df = pd.read_csv('data/IPL_matches.csv')
    
    # Season-wise aggregation
    season_stats = []
    
    for season, group in df.groupby('season'):
        if pd.isna(season):
            continue
            
        stats = {
            'season': int(season),
            'matches': len(group),
            'avg_first_innings': round(group['first_innings_runs'].mean(), 1),
            'avg_second_innings': round(group['second_innings_runs'].mean(), 1),
            'avg_total_runs': round((group['first_innings_runs'] + group['second_innings_runs']).mean(), 1),
            'avg_margin_runs': round(group['win_by_runs'].mean(), 1),
            'avg_margin_wickets': round(group['win_by_wickets'].mean(), 1),
        }
        
        # Count batting first wins
        bat_first_wins = 0
        chase_wins = 0
        
        for _, row in group.iterrows():
            if pd.isna(row['toss_decision']) or pd.isna(row['toss_winner']) or pd.isna(row['match_won_by']):
                continue
                
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
            else:
                chase_wins += 1
        
        total = bat_first_wins + chase_wins
        if total > 0:
            stats['bat_first_win_pct'] = round(bat_first_wins / total * 100, 1)
            stats['chase_win_pct'] = round(chase_wins / total * 100, 1)
        else:
            stats['bat_first_win_pct'] = 50.0
            stats['chase_win_pct'] = 50.0
            
        season_stats.append(stats)
    
    # Sort by season
    season_stats.sort(key=lambda x: x['season'])
    
    # Save to JSON
    os.makedirs('webapp/static/data', exist_ok=True)
    with open('webapp/static/data/season_stats.json', 'w') as f:
        json.dump(season_stats, f)
    
    print(f"Generated season stats for {len(season_stats)} seasons")

if __name__ == '__main__':
    generate_season_stats()
