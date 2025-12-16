import pandas as pd
import json
import os

def generate_team_performance():
    """Generate team-wise performance statistics (wins, losses, matches by season)"""
    
    print("Loading match data...")
    df = pd.read_csv('data/IPL_matches.csv')
    
    team_data = {}
    
    # Get all unique teams
    teams = set(df['team1'].dropna()).union(set(df['team2'].dropna()))
    
    print(f"Processing {len(teams)} teams...")
    
    for team in teams:
        # Find all matches where this team played
        team_matches = df[(df['team1'] == team) | (df['team2'] == team)]
        
        # Season-wise performance
        season_perf = []
        
        for season, season_group in team_matches.groupby('season'):
            if pd.isna(season):
                continue
                
            total = len(season_group)
            wins = len(season_group[season_group['match_won_by'] == team])
            losses = total - wins
            
            # Calculate win rate
            win_rate = (wins / total * 100) if total > 0 else 0
            
            season_perf.append({
                'season': int(season),
                'played': total,
                'won': wins,
                'lost': losses,
                'win_rate': round(win_rate, 1)
            })
        
        # Sort by season
        season_perf.sort(key=lambda x: x['season'])
        
        # Overall stats
        total_matches = len(team_matches)
        total_wins = len(team_matches[team_matches['match_won_by'] == team])
        total_losses = total_matches - total_wins
        
        team_data[team] = {
            'overall': {
                'played': total_matches,
                'won': total_wins,
                'lost': total_losses,
                'win_rate': round((total_wins / total_matches * 100) if total_matches > 0 else 0, 1)
            },
            'by_season': season_perf
        }
    
    # Save to JSON
    os.makedirs('webapp/static/data', exist_ok=True)
    with open('webapp/static/data/team_performance.json', 'w') as f:
        json.dump(team_data, f, indent=2)
    
    print(f"Generated performance data for {len(team_data)} teams")
    
    # Print sample
    sample_team = list(team_data.keys())[0]
    print(f"\nSample data for {sample_team}:")
    print(f"  Overall: {team_data[sample_team]['overall']}")
    print(f"  Seasons: {len(team_data[sample_team]['by_season'])}")

if __name__ == '__main__':
    generate_team_performance()
