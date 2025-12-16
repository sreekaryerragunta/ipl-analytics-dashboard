import pandas as pd
import json
import os

def generate_overview_stats():
    """Generate comprehensive overview statistics from ball-by-ball data"""
    
    # Load ball-by-ball data
    print("Loading ball-by-ball data...")
    df = pd.read_csv('data/IPL.csv', low_memory=False)
    
    # Load match-level data for champions
    matches_df = pd.read_csv('data/IPL_matches.csv')
    
    stats = {}
    
    # TOTAL RUNS
    stats['total_runs'] = int(df['runs_total'].sum())
    
    # TOTAL WICKETS
    stats['total_wickets'] = int(df['wicket_kind'].notna().sum())
    
    # SIXES AND FOURS
    # runs_batter gives runs scored by batsman (excluding extras)
    # A six is when runs_batter == 6 and it's not from extras
    stats['total_sixes'] = int(len(df[(df['runs_batter'] == 6) & (df['runs_extras'] == 0)]))
    stats['total_fours'] = int(len(df[(df['runs_batter'] == 4) & (df['runs_extras'] == 0)]))
    
    # TOTAL MATCHES
    stats['total_matches'] = int(df['match_id'].nunique())
    
    # SEASONS
    stats['seasons_count'] = int(df['season'].nunique())
    
    # IPL CHAMPIONS BY YEAR
    # Get winners from matches
    champions = {}
    
    # For each season, find the final/most recent matches and the winner
    # We'll use a simplified approach: find the winner with most wins per season
    for season, group in matches_df.groupby('season'):
        if pd.isna(season):
            continue
        
        # Count wins by team
        winner_counts = group['match_won_by'].value_counts()
        
        if len(winner_counts) > 0:
            # Get the team with most wins (likely champion)
            # In reality, we'd need playoff/final data, but this is a reasonable approximation
            # Actually, let's try a different approach: look for the latest match in the season
            
            # Sort by date and get the last match winner
            last_match = group.sort_values('date').iloc[-1]
            champion = last_match['match_won_by']
            
            if pd.notna(champion) and champion != 'Unknown':
                champions[int(season)] = champion
    
    # Manual override for known champions (more accurate)
    # This is based on actual IPL history
    known_champions = {
        2008: 'Rajasthan Royals',
        2009: 'Deccan Chargers',
        2010: 'Chennai Super Kings',
        2011: 'Chennai Super Kings',
        2012: 'Kolkata Knight Riders',
        2013: 'Mumbai Indians',
        2014: 'Kolkata Knight Riders',
        2015: 'Mumbai Indians',
        2016: 'Sunrisers Hyderabad',
        2017: 'Mumbai Indians',
        2018: 'Chennai Super Kings',
        2019: 'Mumbai Indians',
        2020: 'Mumbai Indians',
        2021: 'Chennai Super Kings',
        2022: 'Gujarat Titans',
        2023: 'Chennai Super Kings',
        2024: 'Kolkata Knight Riders',
    }
    
    # Merge with known champions
    champions.update(known_champions)
    
    stats['champions'] = champions
    
    # TOP SCORERS (batsmen with most runs)
    batter_runs = df.groupby('batter')['runs_batter'].sum().sort_values(ascending=False).head(10)
    stats['top_scorers'] = {k: int(v) for k, v in batter_runs.items()}
    
    # TOP WICKET TAKERS
    wicket_takers = df[df['wicket_kind'].notna()].groupby('bowler').size().sort_values(ascending=False).head(10)
    stats['top_wicket_takers'] = {k: int(v) for k, v in wicket_takers.items()}
    
    # Save to JSON
    os.makedirs('webapp/static/data', exist_ok=True)
    with open('webapp/static/data/overview_stats.json', 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"Generated overview stats:")
    print(f"  Total Runs: {stats['total_runs']:,}")
    print(f"  Total Wickets: {stats['total_wickets']:,}")
    print(f"  Total Sixes: {stats['total_sixes']:,}")
    print(f"  Total Fours: {stats['total_fours']:,}")
    print(f"  Total Matches: {stats['total_matches']:,}")
    print(f"  Champions recorded: {len(stats['champions'])}")

if __name__ == '__main__':
    generate_overview_stats()
