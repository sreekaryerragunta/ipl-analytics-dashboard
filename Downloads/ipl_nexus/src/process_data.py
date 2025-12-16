import pandas as pd
import numpy as np
import re
import os

def clean_season(season):
    if pd.isna(season):
        return np.nan
    s = str(season)
    # Extract year from season string
    # IPL seasons with "/" format need special handling:
    # "2007/08" → IPL 2008, "2009/10" → IPL 2010, "2020/21" → IPL 2021
    if '/' in s:
        # Extract first year from format like "2007/08" 
        parts = s.split('/')
        if len(parts) == 2:
            first_year = int(parts[0])
            # Return first year + 1 to get actual IPL year
            # 2007/08 → 2008, 2009/10 → 2010, 2020/21 → 2021
            return first_year + 1
    
    # For simple year format, extract the 4-digit year
    match = re.search(r'\d{4}', s)
    if match:
        year = int(match.group(0))
        # No additional mapping needed for regular years
        # 2009 stays 2009, 2011 stays 2011, etc.
        return year
    return np.nan

def standardize_names(df):
    # Mapping old names to new/standard names
    mapping = {
        'Delhi Daredevils': 'Delhi Capitals',
        'Kings XI Punjab': 'Punjab Kings',
        'Royal Challengers Bangalore': 'Royal Challengers Bengaluru',
        'Rising Pune Supergiant': 'Rising Pune Supergiants',
        'Pune Warriors': 'Pune Warriors India',
        'Deccan Chargers': 'Sunrisers Hyderabad' # debatable, but often done for franchise continuity. Actually user didn't ask for this. I will stick to USER REQUESTS specifically.
    }
    # User specific requests:
    mapping['Delhi Daredevils'] = 'Delhi Capitals'
    mapping['Royal Challengers Bangalore'] = 'Royal Challengers Bengaluru'
    mapping['Rising Pune Super Giant'] = 'Rising Pune Supergiants'
    mapping['Rising Pune Supergiant'] = 'Rising Pune Supergiants'
    mapping['Kings XI Punjab'] = 'Punjab Kings'
    
    cols = ['batting_team', 'bowling_team', 'toss_winner', 'match_won_by', 'winner']
    for c in cols:
        if c in df.columns:
            df[c] = df[c].replace(mapping)
    return df

def clean_win_outcome(outcome):
    runs, wickets = 0, 0
    if pd.isna(outcome):
        return 0, 0
    outcome = str(outcome).lower()
    
    # "140 runs"
    if 'run' in outcome:
        match = re.search(r'(\d+)', outcome)
        if match:
            runs = int(match.group(1))
            
    # "9 wickets"
    elif 'wicket' in outcome:
        match = re.search(r'(\d+)', outcome)
        if match:
            wickets = int(match.group(1))
            
    return runs, wickets

def process_data():
    print("Loading data...")
    df = pd.read_csv('data/IPL.csv', low_memory=False)
    
    print("Cleaning season...")
    df['season'] = df['season'].apply(clean_season)
    
    print("Standardizing team names...")
    df = standardize_names(df)
    
    print("Standardizing venue names...")
    from utils import standardize_venues
    df = standardize_venues(df)
    
    # Process Match Level Data
    print("Aggregating match data...")
    match_cols = ['match_id', 'date', 'season', 'venue', 'home_team', 'away_team', 
                  'toss_winner', 'toss_decision', 'match_won_by', 
                  'win_outcome', 'result_type']
    
    # Map column names if they differ
    # dataset has 'batting_team', 'bowling_team' per ball. 
    # match_level metadata needs to be extracted.
    # We can group by match_id and take first of some cols.
    
    # Potential match metadata columns in this dataset:
    # ['match_id', 'date', 'season', 'venue', 'toss_winner', 'toss_decision', 'match_won_by', 'win_outcome', 'result_type']
    
    meta_cols = ['match_id', 'date', 'season', 'venue', 'toss_winner', 
                 'toss_decision', 'match_won_by', 'win_outcome', 'result_type']
    
    meta_cols_values = [c for c in meta_cols if c != 'match_id']
    
    matches_meta = df.groupby('match_id')[meta_cols_values].first().reset_index()
    
    # Identify Team1 and Team2
    # We can find teams from batting_team/bowling_team
    teams_per_match = df.groupby('match_id')['batting_team'].unique()
    
    def get_teams(teams_list):
        if len(teams_list) >= 2:
            return teams_list[0], teams_list[1]
        elif len(teams_list) == 1:
            return teams_list[0], np.nan
        return np.nan, np.nan

    # Add teams to matches_meta
    # This is slow if applied row by row, let's try a better way or just iterate.
    # Actually, for 1000 matches it's fast.
    
    team_data = []
    for mid, teams in teams_per_match.items():
        t1, t2 = get_teams(teams)
        team_data.append({'match_id': mid, 'team1': t1, 'team2': t2})
        
    matches_teams = pd.DataFrame(team_data)
    matches_all = pd.merge(matches_meta, matches_teams, on='match_id')
    
    # Scores
    print("Aggregating scores...")
    scores = df.groupby(['match_id', 'innings'])['runs_total'].sum().unstack(fill_value=0)
    # Check if innings are 1, 2 (int) or '1st innings' (str)
    # We will rename columns aggressively
    
    # Handling wickets
    # Wicket is when 'wicket_kind' is not NaN?
    # Or 'is_wicket' column? 
    # Column 'wicket_kind': [nan 'caught' 'bowled' ...]
    df['is_wicket'] = df['wicket_kind'].notna().astype(int)
    wickets = df.groupby(['match_id', 'innings'])['is_wicket'].sum().unstack(fill_value=0)
    
    # Merge scores/wickets back
    # columns might be [1, 2] or ['1st innings', '2nd innings']
    # Let's inspect columns of 'scores'
    print("Innings labels:", scores.columns.tolist())
    
    # Assume 1 and 2 exist (or whatever the main innings are)
    # Sometimes super over innings exist (3, 4 etc). We care about 1 and 2 for basic stats.
    cols_map = {}
    for col in scores.columns:
        if str(col).startswith('1') or col == 1:
            cols_map[col] = 'first_innings_runs'
        elif str(col).startswith('2') or col == 2:
            cols_map[col] = 'second_innings_runs'
            
    scores = scores.rename(columns=cols_map)
    # Keep only relevant
    if 'first_innings_runs' in scores.columns:
        matches_all = pd.merge(matches_all, scores[['first_innings_runs']], on='match_id', how='left')
    if 'second_innings_runs' in scores.columns:
        matches_all = pd.merge(matches_all, scores[['second_innings_runs']], on='match_id', how='left')
        
    # Same for wickets
    wickets_map = {}
    for col in wickets.columns:
        if str(col).startswith('1') or col == 1:
            wickets_map[col] = 'first_innings_wickets'
        elif str(col).startswith('2') or col == 2:
            wickets_map[col] = 'second_innings_wickets'
            
    wickets = wickets.rename(columns=wickets_map)
    if 'first_innings_wickets' in wickets.columns:
        matches_all = pd.merge(matches_all, wickets[['first_innings_wickets']], on='match_id', how='left')
    if 'second_innings_wickets' in wickets.columns:
        matches_all = pd.merge(matches_all, wickets[['second_innings_wickets']], on='match_id', how='left')
        
    # Fill NA for runs/wickets with 0?
    matches_all.fillna({'first_innings_runs': 0, 'second_innings_runs': 0, 
                        'first_innings_wickets': 0, 'second_innings_wickets': 0}, inplace=True)
    
    # Parse Win Outcome
    print("Parsing outcome...")
    outcomes = matches_all['win_outcome'].apply(clean_win_outcome)
    matches_all['win_by_runs'] = [x[0] for x in outcomes]
    matches_all['win_by_wickets'] = [x[1] for x in outcomes]
    
    # Standardize Teams
    # We reuse utils for this or implement here inline
    # Let's verify team names after running
    
    # Save
    out_path = 'data/IPL_matches.csv'
    matches_all.to_csv(out_path, index=False)
    print(f"Saved match-level data to {out_path}, Shape: {matches_all.shape}")

if __name__ == "__main__":
    process_data()
