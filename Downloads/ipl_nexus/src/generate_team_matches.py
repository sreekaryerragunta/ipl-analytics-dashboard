import pandas as pd
import json
import os

def generate_team_matches():
    """Generate detailed match-by-match data for each team grouped by season"""
    
    print("Loading match data...")
    df = pd.read_csv('data/IPL_matches.csv')
    
    teams = set(df['team1'].dropna()).union(set(df['team2'].dropna()))
    
    team_matches_data = {}
    
    for team in teams:
        print(f"Processing matches for {team}...")
        
        # Get all matches for this team
        team_matches = df[(df['team1'] == team) | (df['team2'] == team)].copy()
        
        # Group by season
        season_matches = {}
        for season in sorted(team_matches['season'].dropna().unique()):
            season_matches_list = []
            season_df = team_matches[team_matches['season'] == season].sort_values('date')
            
            for _, match in season_df.iterrows():
                # Determine opponent
                opponent = match['team2'] if match['team1'] == team else match['team1']
                
                # Determine if team batted first
                if pd.notna(match['toss_decision']) and pd.notna(match['toss_winner']):
                    if match['toss_decision'] == 'bat':
                        batted_first = (match['toss_winner'] == team)
                    else:
                        batted_first = (match['toss_winner'] != team)
                else:
                    batted_first = None
                
                # Get team score and opponent score
                # This requires knowing which team is which in the match
                is_team1 = (match['team1'] == team)
                
                # Determine result
                won = (match['match_won_by'] == team)
                result = "Won" if won else "Lost"
                
                # Get margin from win_outcome column
                margin = str(match.get('win_outcome', 'Unknown'))
                if pd.isna(match.get('win_outcome')):
                    margin = 'Unknown'
                
                match_info = {
                    'date': str(match['date']) if pd.notna(match['date']) else 'Unknown',
                    'opponent': str(opponent) if pd.notna(opponent) else 'Unknown',
                    'venue': str(match['venue']) if pd.notna(match['venue']) else 'Unknown',
                    'toss_winner': str(match['toss_winner']) if pd.notna(match['toss_winner']) else 'Unknown',
                    'toss_decision': str(match['toss_decision']) if pd.notna(match['toss_decision']) else 'Unknown',
                    'batting_first': batted_first,
                    'result': result,
                    'margin': str(margin),
                    'won': won,
                    'team_is_home': is_team1
                }
                
                season_matches_list.append(match_info)
            
            season_matches[str(int(season))] = season_matches_list
        
        team_matches_data[team] = season_matches
    
    # Save to JSON
    os.makedirs('webapp/static/data', exist_ok=True)
    with open('webapp/static/data/team_matches.json', 'w') as f:
        json.dump(team_matches_data, f, indent=2)
    
    print(f"\nGenerated match data for {len(team_matches_data)} teams")
    
    # Print sample
    sample_team = list(team_matches_data.keys())[0]
    sample_season = list(team_matches_data[sample_team].keys())[0]
    print(f"\nSample for {sample_team} in {sample_season}:")
    print(f"  Total matches: {len(team_matches_data[sample_team][sample_season])}")
    if team_matches_data[sample_team][sample_season]:
        print(f"  First match: {team_matches_data[sample_team][sample_season][0]}")

if __name__ == '__main__':
    generate_team_matches()
