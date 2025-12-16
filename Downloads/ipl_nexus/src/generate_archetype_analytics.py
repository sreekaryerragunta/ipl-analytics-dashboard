import pandas as pd
import json
import os

# Load existing archetypes data
with open('webapp/static/data/archetypes.json', 'r') as f:
    archetypes_data = json.load(f)

# Load ball-by-ball data for player stats
print("Loading ball-by-ball data...")
df_balls = pd.read_csv('data/IPL.csv', low_memory=False)

# Load matches data for toss info
df_matches = pd.read_csv('data/IPL_matches.csv')

print(f"Loaded {len(df_balls)} balls and {len(df_matches)} matches")

# Create match_id to cluster mapping
match_cluster_map = {m['id']: m['cluster'] for m in archetypes_data['matches']}

# Add cluster to balls dataframe
df_balls['cluster'] = df_balls['match_id'].astype(str).map(match_cluster_map)
df_balls = df_balls[df_balls['cluster'].notna()]

# Add season info to balls
match_season_map = {m['id']: m['season'] for m in archetypes_data['matches']}
df_balls['season'] = df_balls['match_id'].astype(str).map(match_season_map)

print(f"Processing {len(df_balls)} balls with cluster assignments...")

# Get distinct seasons for period calculation
all_seasons = sorted([m['season'] for m in archetypes_data['matches']], reverse=True)
last3_cutoff = all_seasons[2] if len(all_seasons) > 2 else all_seasons[0]
last5_cutoff = all_seasons[4] if len(all_seasons) > 4 else all_seasons[0]

def calculate_player_stats(cluster_balls):
    """Calculate player stats for given ball data"""
    # Top Batsmen
    batsman_stats = cluster_balls.groupby('batter').agg({
        'runs_batter': 'sum',
        'ball': 'count',
        'match_id': 'nunique'
    }).reset_index()
    batsman_stats.columns = ['player', 'runs', 'balls', 'matches']
    batsman_stats['sr'] = (batsman_stats['runs'] / batsman_stats['balls'] * 100).round(1)
    
    fours_dict = cluster_balls[cluster_balls['runs_batter'] == 4].groupby('batter').size().to_dict()
    sixes_dict = cluster_balls[cluster_balls['runs_batter'] == 6].groupby('batter').size().to_dict()
    
    batsman_stats['fours'] = batsman_stats['player'].map(lambda p: fours_dict.get(p, 0))
    batsman_stats['sixes'] = batsman_stats['player'].map(lambda p: sixes_dict.get(p, 0))
    
    top_batsmen = batsman_stats.nlargest(10, 'runs')[['player', 'runs', 'balls', 'sr', 'fours', 'sixes', 'matches']].to_dict('records')
    
    # Top Bowlers
    bowler_stats = cluster_balls.groupby('bowler').agg({
        'runs_total': 'sum',
        'ball': 'count',
        'wicket_kind': lambda x: x.notna().sum(),
        'match_id': 'nunique'
    }).reset_index()
    bowler_stats.columns = ['player', 'runs', 'balls', 'wickets', 'matches']
    bowler_stats['economy'] = (bowler_stats['runs'] / (bowler_stats['balls'] / 6)).round(2)
    
    dots = cluster_balls[cluster_balls['runs_total'] == 0].groupby('bowler').size().to_dict()
    bowler_stats['dots'] = bowler_stats['player'].map(lambda p: dots.get(p, 0))
    
    top_bowlers = bowler_stats.nlargest(10, 'wickets')[['player', 'wickets', 'runs', 'balls', 'economy', 'dots', 'matches']].to_dict('records')
    
    return top_batsmen, top_bowlers

def calculate_toss_impact(cluster_matches_df):
    """Calculate toss impact for given matches"""
    total = len(cluster_matches_df)
    if total == 0:
        return None
        
    toss_winner_won = len(cluster_matches_df[cluster_matches_df['toss_winner'] == cluster_matches_df['match_won_by']])
    toss_win_pct = round((toss_winner_won / total * 100), 1)
    
    bat_first = cluster_matches_df[cluster_matches_df['toss_decision'] == 'bat']
    field_first = cluster_matches_df[cluster_matches_df['toss_decision'] == 'field']
    
    bat_first_wins = len(bat_first[bat_first['toss_winner'] == bat_first['match_won_by']])
    field_first_wins = len(field_first[field_first['toss_winner'] == field_first['match_won_by']])
    
    bat_first_win_pct = round((bat_first_wins / len(bat_first) * 100), 1) if len(bat_first) > 0 else 0
    field_first_win_pct = round((field_first_wins / len(field_first) * 100), 1) if len(field_first) > 0 else 0
    
    return {
        'total_matches': total,
        'toss_winner_won': toss_winner_won,
        'toss_win_pct': toss_win_pct,
        'bat_first_count': len(bat_first),
        'bat_first_win_pct': bat_first_win_pct,
        'field_first_count': len(field_first),
        'field_first_win_pct': field_first_win_pct
    }

def calculate_venue_stats(cluster_matches):
    """Calculate venue stats for given matches"""
    venue_stats_list = []
    venue_groups = {}
    
    # Group matches by venue
    for match in cluster_matches:
        venue = match['venue']
        if venue not in venue_groups:
            venue_groups[venue] = []
        venue_groups[venue].append(match)
    
    # Calculate stats for each venue
    for venue, venue_matches in venue_groups.items():
        avg_score1 = round(sum(m['score1'] for m in venue_matches) / len(venue_matches))
        avg_score2 = round(sum(m['score2'] for m in venue_matches) / len(venue_matches))
        chases_won = sum(1 for m in venue_matches if m['score2'] > m['score1'])
        chase_success = round((chases_won / len(venue_matches) * 100), 1)
        
        venue_stats_list.append({
            'venue': venue,
            'matches': len(venue_matches),
            'avg_score1': avg_score1,
            'avg_score2': avg_score2,
            'chase_success': chase_success
        })
    
    # Sort by match count (descending)
    venue_stats_list.sort(key=lambda x: x['matches'], reverse=True)
    return venue_stats_list  # Return all venues, no limit

# Initialize cluster analytics with period breakdowns
cluster_analytics = {}

for cluster_id in range(4):
    print(f"\nProcessing Cluster {cluster_id}...")
    
    cluster_matches = [m for m in archetypes_data['matches'] if m['cluster'] == cluster_id]
    match_ids_int = [int(m['id']) for m in cluster_matches]
    
    # Get recent seasons for individual analytics
    recent_seasons = [2023, 2024, 2025]
    
    # Period-specific analytics
    periods = {
        'overall': cluster_matches,
        'last3': [m for m in cluster_matches if m['season'] >= last3_cutoff],
        'last5': [m for m in cluster_matches if m['season'] >= last5_cutoff]
    }
    
    # Add individual recent seasons
    for season in recent_seasons:
        season_matches = [m for m in cluster_matches if m['season'] == season]
        if len(season_matches) > 0:
            periods[f'season_{season}'] = season_matches
    
    cluster_analytics[cluster_id] = {}
    
    for period_name, period_matches in periods.items():
        if len(period_matches) == 0:
            continue
            
        print(f"  - {period_name}: {len(period_matches)} matches")
        
        # Filter balls for this period
        period_match_ids = [m['id'] for m in period_matches]
        period_balls = df_balls[df_balls['match_id'].astype(str).isin(period_match_ids)]
        
        # Calculate stats
        top_batsmen, top_bowlers = calculate_player_stats(period_balls)
        
        # Toss impact
        period_match_ids_int = [int(m['id']) for m in period_matches]
        toss_matches = df_matches[df_matches['match_id'].isin(period_match_ids_int)]
        toss_impact = calculate_toss_impact(toss_matches)
        
        # Venue stats
        venue_stats = calculate_venue_stats(period_matches)
        
        cluster_analytics[cluster_id][period_name] = {
            'top_batsmen': top_batsmen,
            'top_bowlers': top_bowlers,
            'toss_impact': toss_impact,
            'venue_stats': venue_stats
        }

# Save enriched data
output = {
    'meta': archetypes_data['meta'],
    'matches': archetypes_data['matches'],
    'analytics': cluster_analytics
}

output_file = 'webapp/static/data/archetypes_detailed.json'
with open(output_file, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nSaved enriched archetype analytics to {output_file}")
print(f"  - Generated stats for 4 clusters across 3 periods (overall, last3, last5)")
print(f"  - Player stats, toss metrics, and venue analytics included")
