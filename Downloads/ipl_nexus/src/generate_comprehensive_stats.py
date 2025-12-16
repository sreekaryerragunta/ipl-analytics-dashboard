import pandas as pd
import json
import os
import numpy as np
from collections import defaultdict

print("="*80)
print("IPL COMPREHENSIVE STATS GENERATOR")
print("="*80)

# Load data
print("\nLoading data...")
df_balls = pd.read_csv('data/IPL.csv', low_memory=False)
df_matches = pd.read_csv('data/IPL_matches.csv')

print(f"[OK] Loaded {len(df_balls):,} ball records")
print(f"[OK] Loaded {len(df_matches):,} matches")
print(f"[OK] Seasons: {df_matches['season'].min()} to {df_matches['season'].max()}")

# Create output directory
os.makedirs('webapp/static/data/stats', exist_ok=True)

# CRITICAL: Replace all NaN values in source data to prevent JSON errors
print("Cleaning NaN values from source data...")
df_balls = df_balls.fillna({
    'runs_batter': 0,
    'runs_total': 0,
    'runs_extras': 0,
    'wicket_kind': '',
    'player_out': '',
    'batter': 'Unknown',
    'bowler': 'Unknown',
    'batting_team': 'Unknown',
    'season': 0
})

df_matches = df_matches.fillna({
    'team1': 'Unknown',
    'team2': 'Unknown',
    'match_won_by': '',
    'toss_winner': '',
    'first_innings_runs': 0,
    'second_innings_runs': 0,
    'win_by_runs': 0,
    'win_by_wickets': 0,
    'result_type': 'normal'
})

# Remove any rows where critical fields are still Unknown/empty after fillna
df_balls = df_balls[df_balls['batter'] != 'Unknown']
df_balls = df_balls[df_balls['bowler'] != 'Unknown']
df_matches = df_matches[df_matches['team1'] != 'Unknown']
df_matches = df_matches[df_matches['team2'] != 'Unknown']

print(f"[OK] Cleaned data: {len(df_balls):,} balls, {len(df_matches):,} matches")

# Helper function to clean data before JSON dump
def clean_for_json(obj):
    """Recursively replace NaN/inf with None for JSON compatibility"""
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(item) for item in obj]
    elif isinstance(obj, float):
        if pd.isna(obj) or obj == float('inf') or obj == float('-inf'):
            return 0.0
        return obj
    return obj

# Custom JSON encoder
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            if np.isnan(obj) or np.isinf(obj):
                return 0.0
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


# Helper function for season filtering
def filter_by_season(df, period='overall', season=None):
    """Filter dataframe by season period"""
    if season:
        return df[df['season'] == int(season)]
    elif period == 'last3':
        return df[df['season'] >= 2023]
    elif period == 'last5':
        return df[df['season'] >= 2021]
    else:  # overall
        return df

# ============================================================================
# 1. SERIES & POINTS TABLES
# ============================================================================
print("\n" + "="*80)
print("1. GENERATING SERIES & POINTS TABLE RECORDS")
print("="*80)

points_tables = {}
series_stats = {}

for season in sorted(df_matches['season'].unique()):
    season_matches = df_matches[df_matches['season'] == season]
    
    # Filter out NaN teams
    teams_list = season_matches['team1'].dropna().tolist() + season_matches['team2'].dropna().tolist()
    teams = set([t for t in teams_list if pd.notna(t) and t != ''])
    
    standings = {}
    
    for team in teams:
        team_matches = season_matches[(season_matches['team1'] == team) | (season_matches['team2'] == team)]
        wins = len(team_matches[team_matches['match_won_by'] == team])
        total = len(team_matches)
        losses = total - wins - len(team_matches[team_matches['result_type'] == 'no result'])
        no_result = len(team_matches[team_matches['result_type'] == 'no result'])
        
        standings[team] = {
            'team': str(team),
            'matches': total,
            'wins': wins,
            'losses': losses,
            'no_result': no_result,
            'points': wins * 2 + no_result,
            'nrr': 0.0  # Simplified for now
        }
    
    standings_list = sorted(standings.values(), key=lambda x: (-x['points'], -x['wins']))
    points_tables[str(int(season))] = standings_list
    
    series_stats[str(int(season))] = {
        'season': int(season),
        'total_matches': len(season_matches),
        'teams': len(teams),
        'winner': standings_list[0]['team'] if standings_list else None
    }

series_records = {
    'points_tables': points_tables,
    'series_stats': series_stats
}

with open('webapp/static/data/stats/series_records.json', 'w') as f:
    json.dump(clean_for_json(series_records), f, indent=2, cls=NpEncoder)
print(f"[OK] Generated points tables for {len(points_tables)} seasons")

# ============================================================================
# 2. PLAYER PROFILES
# ============================================================================
print("\n" + "="*80)
print("2. GENERATING PLAYER PROFILES")
print("="*80)

# Get all unique players
batsmen = set(df_balls['batter'].dropna().unique())
bowlers = set(df_balls['bowler'].dropna().unique())
all_players = batsmen | bowlers

player_profiles = []

for player in all_players:
    profile = {'player': player}
    
    # Batting stats
    player_batting = df_balls[df_balls['batter'] == player]
    if len(player_batting) > 0:
        runs = player_batting['runs_batter'].sum()
        balls = len(player_batting)
        matches = player_batting['match_id'].nunique()
        dismissals = len(df_balls[(df_balls['player_out'] == player) & (df_balls['wicket_kind'].notna())])
        
        profile['batting'] = {
            'runs': int(runs),
            'balls': int(balls),
            'matches': int(matches),
            'avg': float(round(runs / dismissals, 2)) if dismissals > 0 else float(runs),
            'sr': float(round(runs / balls * 100, 2)) if balls > 0 else 0.0,
            'fours': int(len(player_batting[player_batting['runs_batter'] == 4])),
            'sixes': int(len(player_batting[player_batting['runs_batter'] == 6]))
        }
    
    # Bowling stats
    player_bowling = df_balls[df_balls['bowler'] == player]
    if len(player_bowling) > 0:
        wickets = len(player_bowling[player_bowling['wicket_kind'].notna()])
        runs_conceded = player_bowling['runs_total'].sum()
        balls_bowled = len(player_bowling)
        matches = player_bowling['match_id'].nunique()
        
        profile['bowling'] = {
            'wickets': int(wickets),
            'runs': int(runs_conceded),
            'balls': int(balls_bowled),
            'matches': int(matches),
            'avg': float(round(runs_conceded / wickets, 2)) if wickets > 0 else 0.0,
            'sr': float(round(balls_bowled / wickets, 2)) if wickets > 0 else 0.0,
            'economy': float(round(runs_conceded / (balls_bowled / 6), 2)) if balls_bowled > 0 else 0.0
        }
    
    player_profiles.append(profile)

with open('webapp/static/data/stats/player_profiles.json', 'w') as f:
    json.dump(clean_for_json(player_profiles), f, indent=2, cls=NpEncoder)
print(f"[OK] Generated profiles for {len(player_profiles)} players")

# ============================================================================
# 3. TEAM RECORDS
# ============================================================================
print("\n" + "="*80)
print("3. GENERATING TEAM RECORDS")
print("="*80)

# Filter out NaN values from team names
teams_list = df_matches['team1'].dropna().tolist() + df_matches['team2'].dropna().tolist()
teams = set([t for t in teams_list if pd.notna(t)])

team_records = {}

for team in teams:
    team_matches = df_matches[(df_matches['team1'] == team) | (df_matches['team2'] == team)]
    wins = len(team_matches[team_matches['match_won_by'] == team])
    
    team_records[team] = {
        'team': team,
        'matches': len(team_matches),
        'wins': wins,
        'losses': len(team_matches) - wins - len(team_matches[team_matches['result_type'] == 'no result']),
        'win_pct': round(wins / len(team_matches) * 100, 2) if len(team_matches) > 0 else 0.0
    }

# Head to head matrix - only include valid teams
h2h_matrix = {}
for team1 in teams:
    if pd.isna(team1):
        continue
    h2h_matrix[team1] = {}
    for team2 in teams:
        if pd.isna(team2) or team1 == team2:
            continue
        h2h_matches = df_matches[
            ((df_matches['team1'] == team1) & (df_matches['team2'] == team2)) |
            ((df_matches['team1'] == team2) & (df_matches['team2'] == team1))
        ]
        wins = len(h2h_matches[h2h_matches['match_won_by'] == team1])
        h2h_matrix[team1][team2] = {
            'matches': len(h2h_matches),
            'wins': wins,
            'losses': len(h2h_matches) - wins
        }

team_data = {
    'team_records': team_records,
    'head_to_head': h2h_matrix
}

with open('webapp/static/data/stats/team_records.json', 'w') as f:
    json.dump(clean_for_json(team_data), f, indent=2, cls=NpEncoder)
print(f"[OK] Generated records for {len(teams)} teams")

# ============================================================================
# 4. GROUND RECORDS
# ============================================================================
print("\n" + "="*80)
print("4. GENERATING GROUND RECORDS")
print("="*80)

venues = df_matches['venue'].unique()
ground_records = []

for venue in venues:
    venue_matches = df_matches[df_matches['venue'] == venue]
    
    # Get non-zero scores for safer min calculations
    first_innings_scores = venue_matches[venue_matches['first_innings_runs'] > 0]['first_innings_runs']
    second_innings_scores = venue_matches[venue_matches['second_innings_runs'] > 0]['second_innings_runs']
    
    ground_records.append({
        'venue': venue,
        'matches': len(venue_matches),
        'avg_first_innings': float(round(venue_matches['first_innings_runs'].mean(), 2)) if len(venue_matches) > 0 and not pd.isna(venue_matches['first_innings_runs'].mean()) else 0.0,
        'avg_second_innings': float(round(venue_matches['second_innings_runs'].mean(), 2)) if len(venue_matches) > 0 and not pd.isna(venue_matches['second_innings_runs'].mean()) else 0.0,
        'highest_total': int(venue_matches['first_innings_runs'].max()) if len(venue_matches) > 0 and not pd.isna(venue_matches['first_innings_runs'].max()) else 0,
        'lowest_total': int(first_innings_scores.min()) if len(first_innings_scores) > 0 and not pd.isna(first_innings_scores.min()) else 0
    })

with open('webapp/static/data/stats/ground_records.json', 'w') as f:
    json.dump(clean_for_json(ground_records), f, indent=2, cls=NpEncoder)
print(f"[OK] Generated records for {len(ground_records)} venues")

# ============================================================================
# 5. MATCH RECORDS
# ============================================================================
print("\n" + "="*80)
print("5. GENERATING MATCH RECORDS")
print("="*80)

# Tied matches
tied_matches = df_matches[df_matches['result_type'] == 'tie'].copy()
tied_records = []
for _, match in tied_matches.iterrows():
    tied_records.append({
        'match_id': int(match['match_id']),
        'date': str(match['date']),
        'team1': match['team1'],
        'team2': match['team2'],
       'venue': match['venue'],
        'season': int(match['season']),
        'score': int(match['first_innings_runs']) if pd.notna(match['first_innings_runs']) else 0
    })

# Narrow margins
narrow_wins = df_matches[
    ((df_matches['win_by_runs'] > 0) & (df_matches['win_by_runs'] < 5)) |
    ((df_matches['win_by_wickets'] > 0) & (df_matches['win_by_wickets'] <= 2))
].copy()

narrow_records = []
for _, match in narrow_wins.head(50).iterrows():
    narrow_records.append({
        'match_id': int(match['match_id']),
        'date': str(match['date']),
        'winner': match['match_won_by'],
        'margin': f"{int(match['win_by_runs'])} runs" if match['win_by_runs'] > 0 else f"{int(match['win_by_wickets'])} wickets",
        'team1': match['team1'],
        'team2': match['team2'],
        'venue': match['venue'],
        'season': int(match['season'])
    })

# Wide margins
wide_wins = df_matches[
    (df_matches['win_by_runs'] > 100) | (df_matches['win_by_wickets'] >= 9)
].copy()

wide_records = []
for _, match in wide_wins.head(50).iterrows():
    wide_records.append({
        'match_id': int(match['match_id']),
        'date': str(match['date']),
        'winner': match['match_won_by'],
        'margin': f"{int(match['win_by_runs'])} runs" if match['win_by_runs'] > 0 else f"{int(match['win_by_wickets'])} wickets",
        'team1': match['team1'],
        'team2': match['team2'],
        'venue': match['venue'],
        'season': int(match['season'])
    })

# Close chases
close_chases = df_matches[
    (df_matches['win_by_wickets'] > 0) &
    (df_matches['win_by_wickets'] <= 3) &
    (df_matches['first_innings_runs'] >= 150)
].copy()

chase_records = []
for _, match in close_chases.head(50).iterrows():
    chase_records.append({
        'match_id': int(match['match_id']),
        'date': str(match['date']),
        'winner': match['match_won_by'],
        'target': int(match['first_innings_runs']),
        'wickets_left': int(match['win_by_wickets']),
        'team1': match['team1'],
        'team2': match['team2'],
        'venue': match['venue'],
        'season': int(match['season'])
    })

match_records = {
    'tied_matches': tied_records,
    'narrow_wins': narrow_records,
    'wide_wins': wide_records,
    'close_chases': chase_records
}

with open('webapp/static/data/stats/match_records.json', 'w') as f:
    json.dump(clean_for_json(match_records), f, indent=2, cls=NpEncoder)
print(f"[OK] Generated {len(tied_records)} tied matches, {len(narrow_records)} narrow wins")

# ============================================================================
# 6. SCORING RECORDS
# ============================================================================
print("\n" + "="*80)
print("6. GENERATING SCORING RECORDS")
print("="*80)

# Highest team totals
highest_totals = df_matches.nlargest(50, 'first_innings_runs')[
    ['match_id', 'date', 'season', 'team1', 'team2', 'venue', 'first_innings_runs', 'match_won_by']
].copy()
highest_totals_list = []
for _, row in highest_totals.iterrows():
    highest_totals_list.append({
        'team': row['team1'],
        'score': int(row['first_innings_runs']),
        'opponent': row['team2'],
        'venue': row['venue'],
        'season': int(row['season']),
        'date': str(row['date']),
        'won': row['match_won_by'] == row['team1']
    })

# Lowest totals (excluding 0s)
lowest_totals = df_matches[df_matches['first_innings_runs'] > 0].nsmallest(50, 'first_innings_runs')[
    ['match_id', 'date', 'season', 'team1', 'team2', 'venue', 'first_innings_runs', 'match_won_by']
].copy()
lowest_totals_list = []
for _, row in lowest_totals.iterrows():
    lowest_totals_list.append({
        'team': row['team1'],
        'score': int(row['first_innings_runs']),
        'opponent': row['team2'],
        'venue': row['venue'],
        'season': int(row['season']),
        'date': str(row['date'])
    })

# Highest match aggregates
df_matches['match_aggregate'] = df_matches['first_innings_runs'] + df_matches['second_innings_runs']
highest_aggregates = df_matches.nlargest(50, 'match_aggregate')[
    ['match_id', 'date', 'season', 'team1', 'team2', 'venue', 'first_innings_runs', 'second_innings_runs', 'match_aggregate']
].copy()
aggregate_list = []
for _, row in highest_aggregates.iterrows():
    aggregate_list.append({
        'total': int(row['match_aggregate']),
        'team1': row['team1'],
        'score1': int(row['first_innings_runs']),
        'team2': row['team2'],
        'score2': int(row['second_innings_runs']),
        'venue': row['venue'],
        'season': int(row['season']),
        'date': str(row['date'])
    })

# Highest successful chases
successful_chases = df_matches[df_matches['win_by_wickets'] > 0].nlargest(50, 'first_innings_runs')[
    ['match_id', 'date', 'season', 'team1', 'team2', 'venue', 'first_innings_runs', 'match_won_by', 'win_by_wickets']
].copy()
chase_list = []
for _, row in successful_chases.iterrows():
    chase_list.append({
        'target': int(row['first_innings_runs']),
        'chasing_team': row['match_won_by'],
        'bowling_team': row['team1'],
        'wickets_left': int(row['win_by_wickets']),
        'venue': row['venue'],
        'season': int(row['season']),
        'date': str(row['date'])
    })

scoring_records = {
    'highest_totals': highest_totals_list,
    'lowest_totals': lowest_totals_list,
    'highest_aggregates': aggregate_list,
    'highest_chases': chase_list
}

with open('webapp/static/data/stats/scoring_records.json', 'w') as f:
    json.dump(clean_for_json(scoring_records), f, indent=2, cls=NpEncoder)
print("[OK] Generated scoring records")

# ============================================================================
# 7. PARTNERSHIPS
# ============================================================================
print("\n" + "="*80)
print("7. GENERATING PARTNERSHIP RECORDS")
print("="*80)

# Opening partnerships - calculate from ball-by-ball
opening_partnerships = []

for match_id in df_matches['match_id'].unique():
    match_balls = df_balls[df_balls['match_id'] == match_id]
    
    for innings in [1, 2]:
        innings_balls = match_balls[match_balls['innings'] == innings].sort_values(['over', 'ball'])
        
        if len(innings_balls) == 0:
            continue
        
        batting_team = innings_balls.iloc[0]['batting_team']
        
        # Get runs until first wicket
        first_wicket_idx = innings_balls[innings_balls['wicket_kind'].notna()].index
        
        if len(first_wicket_idx) > 0:
            opening_balls = innings_balls.loc[:first_wicket_idx[0]]
        else:
            opening_balls = innings_balls
        
        partnership_runs = opening_balls['runs_total'].sum()
        
        if partnership_runs > 0:
            batters = opening_balls['batter'].unique()[:2]
            
            # Extract year from season (handles "2007/08" format)
            season_val = innings_balls.iloc[0]['season']
            if isinstance(season_val, str):
                season_year = int(season_val.split('/')[0])
            else:
                season_year = int(season_val)
            
            opening_partnerships.append({
                'runs': int(partnership_runs),
                'team': batting_team,
                'batsmen': list(batters) if len(batters) > 0 else [],
                'match_id': int(match_id),
                'season': season_year
            })

# Sort and get top 50
opening_partnerships_sorted = sorted(opening_partnerships, key=lambda x: x['runs'], reverse=True)[:50]

partnership_records = {
    'opening_partnerships_50plus': [p for p in opening_partnerships_sorted if p['runs'] >= 50],
    'opening_partnerships_100plus': [p for p in opening_partnerships_sorted if p['runs'] >= 100],
    'top_opening_partnerships': opening_partnerships_sorted
}

with open('webapp/static/data/stats/partnership_records.json', 'w') as f:
    json.dump(clean_for_json(partnership_records), f, indent=2, cls=NpEncoder)
print(f"[OK] Generated {len(opening_partnerships_sorted)} opening partnership records")

# ============================================================================
# 8. BATTING RECORDS
# ============================================================================
print("\n" + "="*80)
print("8. GENERATING BATTING RECORDS")
print("="*80)

# Career batting stats
batting_stats = df_balls.groupby('batter').agg({
    'runs_batter': 'sum',
    'ball': 'count',
    'match_id': 'nunique'
}).reset_index()
batting_stats.columns = ['player', 'runs', 'balls', 'matches']
batting_stats['sr'] = (batting_stats['runs'] / batting_stats['balls'] * 100).round(2)

# Get dismissals
dismissals = df_balls[df_balls['wicket_kind'].notna() & (df_balls['player_out'] == df_balls['batter'])].groupby('batter').size()
batting_stats['dismissals'] = batting_stats['player'].map(dismissals).fillna(0).astype(int)
batting_stats['avg'] = (batting_stats['runs'] / batting_stats['dismissals'].replace(0, 1)).round(2)

# Boundaries
fours = df_balls[df_balls['runs_batter'] == 4].groupby('batter').size()
sixes = df_balls[df_balls['runs_batter'] == 6].groupby('batter').size()
batting_stats['fours'] = batting_stats['player'].map(fours).fillna(0).astype(int)
batting_stats['sixes'] = batting_stats['player'].map(sixes).fillna(0).astype(int)

# Most runs
most_runs = batting_stats.nlargest(100, 'runs').to_dict('records')

# Highest averages (min 20 innings)
highest_avg = batting_stats[batting_stats['matches'] >= 20].nlargest(50, 'avg').to_dict('records')

# Best strike rates (min 20 innings)
best_sr = batting_stats[batting_stats['matches'] >= 20].nlargest(50, 'sr').to_dict('records')

# Most sixes
most_sixes = batting_stats.nlargest(50, 'sixes')[['player', 'sixes', 'matches', 'runs']].to_dict('records')

# Most fours
most_fours = batting_stats.nlargest(50, 'fours')[['player', 'fours', 'matches', 'runs']].to_dict('records')

# Innings-based records
innings_scores = df_balls.groupby(['match_id', 'batter']).agg({
    'runs_batter': 'sum',
    'ball': 'count'
}).reset_index()
innings_scores.columns = ['match_id', 'player', 'runs', 'balls']
innings_scores['sr'] = (innings_scores['runs'] / innings_scores['balls'] * 100).round(2)

# Add match details
match_details = df_matches[['match_id', 'season', 'date', 'team1', 'team2', 'venue']].copy()
innings_scores = innings_scores.merge(match_details, on='match_id', how='left')

# Highest scores
highest_scores = innings_scores.nlargest(100, 'runs').to_dict('records')

# Fastest 50s
fastest_fifties = innings_scores[innings_scores['runs'] >= 50].nsmallest(50, 'balls')[
    ['player', 'runs', 'balls', 'sr', 'season', 'team1', 'team2', 'venue']
].to_dict('records')

# Fastest 100s
fastest_hundreds = innings_scores[innings_scores['runs'] >= 100].nsmallest(30, 'balls')[
    ['player', 'runs', 'balls', 'sr', 'season', 'team1', 'team2', 'venue']
].to_dict('records')

batting_records = {
    'most_runs': most_runs,
    'highest_avg': highest_avg,
    'best_sr': best_sr,
    'most_sixes': most_sixes,
    'most_fours': most_fours,
    'highest_scores': highest_scores,
    'fastest_fifties': fastest_fifties,
    'fastest_hundreds': fastest_hundreds
}

with open('webapp/static/data/stats/batting_records.json', 'w') as f:
    json.dump(clean_for_json(batting_records), f, indent=2, cls=NpEncoder)
print(f"[OK] Generated batting records for {len(batting_stats)} players")

# ============================================================================
# 9. BOWLING RECORDS
# ============================================================================
print("\n" + "="*80)
print("9. GENERATING BOWLING RECORDS")
print("="*80)

# Career bowling stats
bowling_stats = df_balls.groupby('bowler').agg({
    'runs_total': 'sum',
    'ball': 'count',
    'wicket_kind': lambda x: x.notna().sum(),
    'match_id': 'nunique'
}).reset_index()
bowling_stats.columns = ['player', 'runs', 'balls', 'wickets', 'matches']
bowling_stats['economy'] = (bowling_stats['runs'] / (bowling_stats['balls'] / 6)).round(2)
bowling_stats['avg'] = (bowling_stats['runs'] / bowling_stats['wickets'].replace(0, 1)).round(2)
bowling_stats['sr'] = (bowling_stats['balls'] / bowling_stats['wickets'].replace(0, 1)).round(2)

# Most wickets
most_wickets = bowling_stats.nlargest(100, 'wickets').to_dict('records')

# Best averages (min 20 wickets)
best_avg = bowling_stats[bowling_stats['wickets'] >= 20].nsmallest(50, 'avg').to_dict('records')

# Best economy (min 20 matches)
best_economy = bowling_stats[bowling_stats['matches'] >= 20].nsmallest(50, 'economy')[
    ['player', 'economy', 'wickets', 'matches']
].to_dict('records')

# Best strike rates (min 20 wickets)
best_bowling_sr = bowling_stats[bowling_stats['wickets'] >= 20].nsmallest(50, 'sr')[
    ['player', 'sr', 'wickets', 'avg', 'matches']
].to_dict('records')

# Innings bowling figures
innings_bowling = df_balls.groupby(['match_id', 'bowler']).agg({
    'runs_total': 'sum',
    'ball': 'count',
    'wicket_kind': lambda x: x.notna().sum()
}).reset_index()
innings_bowling.columns = ['match_id', 'player', 'runs', 'balls', 'wickets']
innings_bowling['economy'] = (innings_bowling['runs'] / (innings_bowling['balls'] / 6)).round(2)
innings_bowling = innings_bowling.merge(match_details, on='match_id', how='left')

# Best bowling figures
best_bowling = innings_bowling.nlargest(50, 'wickets').to_dict('records')

# Most economical spells (min 4 overs)
most_economical = innings_bowling[innings_bowling['balls'] >= 24].nsmallest(50, 'economy')[
    ['player', 'wickets', 'runs', 'balls', 'economy', 'season', 'team1', 'team2', 'venue']
].to_dict('records')

bowling_records = {
    'most_wickets': most_wickets,
    'best_avg': best_avg,
    'best_economy': best_economy,
    'best_sr': best_bowling_sr,
    'best_bowling': best_bowling,
    'most_economical': most_economical,
    'hat_tricks': []
}

with open('webapp/static/data/stats/bowling_records.json', 'w') as f:
    json.dump(clean_for_json(bowling_records), f, indent=2, cls=NpEncoder)
print(f"[OK] Generated bowling records for {len(bowling_stats)} players")

# =========================================================================================
# 10. ALL-ROUNDER & FIELDING RECORDS
# ============================================================================
print("\n" + "="*80)
print("10. GENERATING ALL-ROUNDER & FIELDING RECORDS")
print("="*80)

# Combine batting and bowling stats
allrounder_stats = batting_stats[['player', 'runs', 'matches']].merge(
    bowling_stats[['player', 'wickets']], on='player', how='outer'
).fillna(0)

# Calculate all-rounder index
allrounder_stats['allrounder_index'] = allrounder_stats['runs'] + (allrounder_stats['wickets'] * 20)
allrounder_stats = allrounder_stats[
    (allrounder_stats['runs'] >= 500) & (allrounder_stats['wickets'] >= 20)
].sort_values('allrounder_index', ascending=False)

top_allrounders = allrounder_stats.head(50).to_dict('records')

fielding_records = {
    'top_allrounders': top_allrounders,
    'most_catches': [],
    'wicketkeeper_records': []
}

with open('webapp/static/data/stats/fielding_records.json', 'w') as f:
    json.dump(clean_for_json(fielding_records), f, indent=2, cls=NpEncoder)
print(f"[OK] Generated all-rounder records for {len(top_allrounders)} players")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("STATS GENERATION COMPLETE!")
print("="*80)
print("\nGenerated files:")
print("  [OK] series_records.json")
print("  [OK] player_profiles.json") 
print("  [OK] team_records.json")
print("  [OK] ground_records.json")
print("  [OK] match_records.json")
print("  [OK] scoring_records.json")
print("  [OK] partnership_records.json")
print("  [OK] batting_records.json")
print("  [OK] bowling_records.json")
print("  [OK] fielding_records.json")
print("  [OK] captaincy_records.json (existing)")
print("\nAll comprehensive stats data generated successfully!")
print("="*80)
