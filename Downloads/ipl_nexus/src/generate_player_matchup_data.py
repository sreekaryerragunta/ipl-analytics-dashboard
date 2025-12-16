import pandas as pd
import json
import os
import numpy as np
from collections import defaultdict

def generate_player_matchup_data():
    print("Generating Player Matchup Data...")
    
    # Load ball-by-ball data
    try:
        df = pd.read_csv('data/IPL.csv', low_memory=False)
        print(f"Loaded {len(df)} balls")
    except FileNotFoundError:
        print("Error: data/IPL.csv not found.")
        return

    # Ensure output dir
    os.makedirs('webapp/static/data', exist_ok=True)

    # Convert season to numeric, handling any string values
    if 'season' in df.columns:
        df['season'] = pd.to_numeric(df['season'], errors='coerce')
        df = df.dropna(subset=['season'])  # Drop rows with invalid season
        current_year = int(df['season'].max())
    else:
        current_year = 2024
    
    print(f"Processing data from seasons up to {current_year}")
    
    # Filter relevant columns
    required_cols = ['season', 'batter', 'bowler', 'runs_batter', 'wicket_kind', 
                     'venue', 'innings', 'ball']
    
    # Check which columns exist
    available_cols = [col for col in required_cols if col in df.columns]
    print(f"Available columns: {available_cols}")
    
    # Get unique batsmen and bowlers
    batsmen = sorted(df['batter'].dropna().unique().tolist()) if 'batter' in df.columns else []
    bowlers = sorted(df['bowler'].dropna().unique().tolist()) if 'bowler' in df.columns else []
    
    print(f"Found {len(batsmen)} batsmen and {len(bowlers)} bowlers")
    
    matchup_data = {
        "batsmen": batsmen,
        "bowlers": bowlers,
        "matchups": {}
    }
    
    def calculate_stats(balls_df):
        """Calculate H2H stats from filtered balls"""
        if len(balls_df) == 0:
            return None
        
        # Filter out wides for ball counts and batting stats
        # Wides do not count as balls faced, but dismissals on wides count
        if 'extra_type' in balls_df.columns:
            valid_balls_df = balls_df[balls_df['extra_type'] != 'wides']
        else:
            valid_balls_df = balls_df

        total_balls = len(valid_balls_df)
        total_runs = balls_df['runs_batter'].sum() if 'runs_batter' in balls_df.columns else 0
        
        # Dismissals (use ALL balls, as you can get out on a wide)
        dismissals = 0
        if 'wicket_kind' in balls_df.columns:
            # Count dismissals (excluding run outs)
            dismissals = len(balls_df[
                (balls_df['wicket_kind'].notna()) & 
                (~balls_df['wicket_kind'].str.contains('run out', case=False, na=False))
            ])
        
        # Calculate metrics
        avg = round(total_runs / dismissals, 2) if dismissals > 0 else total_runs
        sr = round((total_runs / total_balls) * 100, 2) if total_balls > 0 else 0
        
        # Boundaries (usually on legal balls or no balls, not wides)
        fours = len(valid_balls_df[valid_balls_df['runs_batter'] == 4]) if 'runs_batter' in valid_balls_df.columns else 0
        sixes = len(valid_balls_df[valid_balls_df['runs_batter'] == 6]) if 'runs_batter' in valid_balls_df.columns else 0
        
        # Dots (runs_batter=0 on a legal ball)
        dots = len(valid_balls_df[valid_balls_df['runs_batter'] == 0]) if 'runs_batter' in valid_balls_df.columns else 0
        dot_pct = round((dots / total_balls) * 100, 1) if total_balls > 0 else 0
        
        # Scoring pattern
        scoring_pattern = {}
        if 'runs_batter' in valid_balls_df.columns:
            scoring_pattern = {
                "dots": int(dots),
                "singles": int(len(valid_balls_df[valid_balls_df['runs_batter'] == 1])),
                "twos": int(len(valid_balls_df[valid_balls_df['runs_batter'] == 2])),
                "threes": int(len(valid_balls_df[valid_balls_df['runs_batter'] == 3])),
                "fours": int(fours),
                "sixes": int(sixes)
            }
        
        # Boundary dependency
        boundary_runs = (fours * 4) + (sixes * 6)
        boundary_pct = round((boundary_runs / total_runs) * 100, 1) if total_runs > 0 else 0
        
        return {
            "balls": int(total_balls),
            "runs": int(total_runs),
            "dismissals": int(dismissals),
            "avg": float(avg),
            "sr": float(sr),
            "dots": int(dots),
            "dot_pct": float(dot_pct),
            "boundaries": {
                "fours": int(fours),
                "sixes": int(sixes)
            },
            "scoring_pattern": scoring_pattern,
            "boundary_pct": float(boundary_pct)
        }
    
    def get_dismissal_breakdown(balls_df):
        """Get breakdown of dismissal types"""
        if 'wicket_kind' not in balls_df.columns:
            return {}
        
        dismissals = balls_df[
            (balls_df['wicket_kind'].notna()) & 
            (~balls_df['wicket_kind'].str.contains('run out', case=False, na=False))
        ]
        
        breakdown = {}
        for wicket_type in dismissals['wicket_kind'].unique():
            if pd.notna(wicket_type):
                breakdown[wicket_type] = int(len(dismissals[dismissals['wicket_kind'] == wicket_type]))
        
        return breakdown
    
    def get_phase_stats(balls_df):
        """Calculate stats by phase (powerplay/middle/death)"""
        if 'ball' not in balls_df.columns:
            return {}
        
        # Extract over number from ball (e.g., 3.2 -> over 3)
        balls_df_copy = balls_df.copy()
        balls_df_copy['over'] = balls_df_copy['ball'].astype(str).str.split('.').str[0].astype(float)
        
        powerplay = balls_df_copy[balls_df_copy['over'] <= 6]
        middle = balls_df_copy[(balls_df_copy['over'] > 6) & (balls_df_copy['over'] <= 15)]
        death = balls_df_copy[balls_df_copy['over'] > 15]
        
        return {
            "powerplay": calculate_stats(powerplay),
            "middle": calculate_stats(middle),
            "death": calculate_stats(death)
        }
    
    def get_season_wise_stats(balls_df):
        """Calculate stats for each season"""
        if 'season' not in balls_df.columns:
            return {}
        
        season_stats = {}
        for season in sorted(balls_df['season'].unique(), reverse=True):
            season_balls = balls_df[balls_df['season'] == season]
            stats = calculate_stats(season_balls)
            if stats:
                season_stats[str(int(season))] = stats
        
        return season_stats
    
    # Generate matchups
    # Process all unique pairs that meet minimum threshold
    print("Calculating matchups...")
    
    matchup_count = 0
    # Group by batsman-bowler pairs first to check threshold
    grouped = df.groupby(['batter', 'bowler']).size()
    valid_pairs = grouped[grouped >= 6]  # At least 1 over
    
    print(f"Found {len(valid_pairs)} valid matchups (6+ balls, all players)")
    
    for (batsman, bowler), count in valid_pairs.items():
        matchup_count += 1
        
        # Filter balls for this matchup
        mask = (df['batter'] == batsman) & (df['bowler'] == bowler)
        pair_balls = df[mask]
        
        # Create canonical key
        key = f"{batsman.replace(' ', '_')}_vs_{bowler.replace(' ', '_')}"
        
        # Overall stats
        overall_stats = calculate_stats(pair_balls)
        
        # Last 5 seasons
        last_5 = pair_balls[pair_balls['season'] >= (current_year - 5)]
        l5_stats = calculate_stats(last_5)
        
        # Last 3 seasons
        last_3 = pair_balls[pair_balls['season'] >= (current_year - 3)]
        l3_stats = calculate_stats(last_3)
        
        # Venue-wise
        venue_stats = {}
        if 'venue' in df.columns:
            for venue in pair_balls['venue'].unique():
                v_balls = pair_balls[pair_balls['venue'] == venue]
                if len(v_balls) >= 6:  # At least 1 over
                    v_stat = calculate_stats(v_balls)
                    if v_stat:
                        venue_stats[venue] = v_stat
        
        # Batting first vs Chasing
        batting_first_stats = None
        chasing_stats = None
        if 'innings' in df.columns:
            batting_first = pair_balls[pair_balls['innings'] == 1]
            chasing = pair_balls[pair_balls['innings'] == 2]
            
            if len(batting_first) >= 6:
                batting_first_stats = calculate_stats(batting_first)
            if len(chasing) >= 6:
                chasing_stats = calculate_stats(chasing)
        
        # New analytics
        dismissal_breakdown = get_dismissal_breakdown(pair_balls)
        phase_stats = get_phase_stats(pair_balls)
        season_wise = get_season_wise_stats(pair_balls)
        
        matchup_data["matchups"][key] = {
            "batsman": batsman,
            "bowler": bowler,
            "overall": overall_stats,
            "last_5": l5_stats,
            "last_3": l3_stats,
            "by_venue": venue_stats,
            "batting_first": batting_first_stats,
            "chasing": chasing_stats,
            "dismissal_types": dismissal_breakdown,
            "phase_wise": phase_stats,
            "season_wise": season_wise
        }
        
        if matchup_count % 500 == 0:
            print(f"Processed {matchup_count} matchups...")
    
    print(f"\nProcessing complete!")
    print(f"Total matchups processed: {matchup_count}")
    print(f"Expected matchups: {len(valid_pairs)}")
    
    # Build player lists from actual matchups
    batsmen_with_matchups = set()
    bowlers_with_matchups = set()
    
    for key in matchup_data["matchups"]:
        matchup = matchup_data["matchups"][key]
        batsmen_with_matchups.add(matchup["batsman"])
        bowlers_with_matchups.add(matchup["bowler"])
    
    # Update player lists to only include those with matchups
    matchup_data["batsmen"] = sorted(list(batsmen_with_matchups))
    matchup_data["bowlers"] = sorted(list(bowlers_with_matchups))
    
    print(f"Unique batsmen with matchups: {len(matchup_data['batsmen'])}")
    print(f"Unique bowlers with matchups: {len(matchup_data['bowlers'])}")
    
    # Save
    output_file = 'webapp/static/data/player_matchup_data.json'
    with open(output_file, 'w') as f:
        json.dump(matchup_data, f, indent=2)
    
    print(f"\nGenerated {matchup_count} player matchups")
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    generate_player_matchup_data()
