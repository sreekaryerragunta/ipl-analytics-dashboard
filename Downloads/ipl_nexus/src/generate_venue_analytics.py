import pandas as pd
import json
import os

def generate_venue_analytics():
    """Generate comprehensive venue analytics including team performance, toss analysis, and characteristics"""
    
    print("Loading data...")
    df = pd.read_csv('data/IPL_matches.csv')
    
    venues = df['venue'].dropna().unique()
    venue_analytics = {}
    
    # Get all teams
    all_teams = set(df['team1'].dropna()).union(set(df['team2'].dropna()))
    
    for venue in venues:
        print(f"Processing {venue}...")
        venue_matches = df[df['venue'] == venue].copy()
        
        if len(venue_matches) == 0:
            continue
            
        venue_data = {
            'venue_name': venue,
            'total_matches': len(venue_matches),
            'seasons_played': sorted([int(s) for s in venue_matches['season'].dropna().unique().tolist()])
        }
        
        # === OVERALL SCORING STATISTICS ===
        venue_data['avg_first_innings'] = int(venue_matches['first_innings_runs'].mean()) if len(venue_matches) > 0 else 0
        venue_data['avg_second_innings'] = int(venue_matches['second_innings_runs'].mean()) if len(venue_matches) > 0 else 0
        venue_data['avg_total_runs'] = int((venue_matches['first_innings_runs'] + venue_matches['second_innings_runs']).mean()) if len(venue_matches) > 0 else 0
        
        # Classify venue type - 3 categories only
        avg_score = venue_data['avg_first_innings']
        if avg_score >= 170:
            venue_type = 'Batting-Friendly'
        elif avg_score >= 155:
            venue_type = 'Balanced'
        else:
            venue_type = 'Bowling-Friendly'
        
        venue_data['venue_type'] = venue_type
        
        # === BAT FIRST VS CHASE (OVERALL) ===
        bat_first_wins = 0
        chase_wins = 0
        
        for _, match in venue_matches.iterrows():
            if pd.notna(match['toss_winner']) and pd.notna(match['toss_decision']) and pd.notna(match['match_won_by']):
                if match['toss_decision'] == 'bat':
                    batted_first = match['toss_winner']
                else:
                    batted_first = match['team2'] if match['toss_winner'] == match['team1'] else match['team1']
                
                if batted_first == match['match_won_by']:
                    bat_first_wins += 1
                elif match['match_won_by'] != 'Unknown':
                    chase_wins += 1
        
        total_decisive = bat_first_wins + chase_wins
        venue_data['bat_first_wins'] = bat_first_wins
        venue_data['chase_wins'] = chase_wins
        venue_data['bat_first_win_pct'] = round((bat_first_wins / total_decisive * 100) if total_decisive > 0 else 0, 1)
        venue_data['chase_win_pct'] = round((chase_wins / total_decisive * 100) if total_decisive > 0 else 0, 1)
        
        # === TOSS ANALYSIS (OVERALL) ===
        toss_wins_match_wins = len(venue_matches[venue_matches['toss_winner'] == venue_matches['match_won_by']])
        toss_matches = len(venue_matches[venue_matches['toss_winner'].notna() & venue_matches['match_won_by'].notna()])
        venue_data['toss_win_match_win_pct'] = round((toss_wins_match_wins / toss_matches * 100) if toss_matches > 0 else 0, 1)
        
        bat_decisions = len(venue_matches[venue_matches['toss_decision'] == 'bat'])
        field_decisions = len(venue_matches[venue_matches['toss_decision'] == 'field'])
        venue_data['toss_bat_decisions'] = bat_decisions
        venue_data['toss_field_decisions'] = field_decisions
        venue_data['toss_bat_pct'] = round((bat_decisions / (bat_decisions + field_decisions) * 100) if (bat_decisions + field_decisions) > 0 else 0, 1)
        
        venue_data['avg_wickets_first_innings'] = round(venue_matches['first_innings_wickets'].mean(), 1) if len(venue_matches) > 0 else 0
        venue_data['avg_wickets_second_innings'] = round(venue_matches['second_innings_wickets'].mean(), 1) if len(venue_matches) > 0 else 0
        
        # === SEASON-WISE MATCH COUNTS (for accurate filtering display) ===
        current_year = pd.Timestamp.now().year
        venue_data['season_match_counts'] = {
            'all': len(venue_matches),
            'last5': len(venue_matches[venue_matches['season'] >= current_year - 5]),
            'last3': len(venue_matches[venue_matches['season'] >= current_year - 3])
        }
        
        # === TEAM PERFORMANCE (ALL-TIME) ===
        team_records = []
        teams = set(venue_matches['team1'].dropna()).union(set(venue_matches['team2'].dropna()))
        
        for team in teams:
            team_venue_matches = venue_matches[(venue_matches['team1'] == team) | (venue_matches['team2'] == team)]
            wins = len(team_venue_matches[team_venue_matches['match_won_by'] == team])
            played = len(team_venue_matches)
            
            if played >= 3:
                team_records.append({
                    'team': team,
                    'played': played,
                    'won': wins,
                    'lost': played - wins,
                    'win_rate': round((wins / played * 100) if played > 0 else 0, 1)
                })
        
        team_records.sort(key=lambda x: (x['win_rate'], x['played']), reverse=True)
        venue_data['team_performance'] = team_records
        
        # === TEAM-SEASON BREAKDOWN (for filtering) ===
        team_season_data = {}
        for team in all_teams:
            team_season_data[team] = {}
            team_matches = venue_matches[(venue_matches['team1'] == team) | (venue_matches['team2'] == team)]
            
            if len(team_matches) == 0:
                continue
                
            # Overall for this team
            team_season_data[team]['all'] = {
                'played': len(team_matches),
                'won': len(team_matches[team_matches['match_won_by'] == team]),
                'seasons': sorted([int(s) for s in team_matches['season'].dropna().unique().tolist()])
            }
            
            # By season range
            current_year = pd.Timestamp.now().year
            for season_filter in ['last3', 'last5']:
                cutoff = current_year - (3 if season_filter == 'last3' else 5)
                recent_matches = team_matches[team_matches['season'] >= cutoff]
                
                if len(recent_matches) > 0:
                    team_season_data[team][season_filter] = {
                        'played': len(recent_matches),
                        'won': len(recent_matches[recent_matches['match_won_by'] == team]),
                        'seasons': sorted([int(s) for s in recent_matches['season'].dropna().unique().tolist()])
                    }
            
            # Per individual season + season-wise breakdown for Team Performance tab
            seasons_breakdown = []
            for season in sorted(team_matches['season'].dropna().unique()):
                season_matches = team_matches[team_matches['season'] == season]
                if len(season_matches) > 0:
                    won = len(season_matches[season_matches['match_won_by'] == team])
                    played = len(season_matches)
                    team_season_data[team][f'season_{int(season)}'] = {
                        'played': played,
                        'won': won,
                        'season': int(season)
                    }
                    seasons_breakdown.append({
                        'year': int(season),
                        'played': played,
                        'won': won,
                        'lost': played - won,
                        'win_rate': round((won / played * 100) if played > 0 else 0, 1)
                    })
            
            # Add to team data for frontend
            if seasons_breakdown:
                team_season_data[team]['seasons_breakdown'] = sorted(seasons_breakdown, key=lambda x: x['year'], reverse=True)
        
        venue_data['team_season_breakdown'] = team_season_data
        
        # === BATTING STATISTICS ===
        batting_stats = {}
        
        # Highest team score
        highest_1st_inn_idx = venue_matches['first_innings_runs'].idxmax()
        highest_2nd_inn_idx = venue_matches['second_innings_runs'].idxmax()
        
        if pd.notna(highest_1st_inn_idx) and pd.notna(highest_2nd_inn_idx):
            highest_1st = venue_matches.loc[highest_1st_inn_idx]
            highest_2nd = venue_matches.loc[highest_2nd_inn_idx]
            
            if highest_1st['first_innings_runs'] >= highest_2nd['second_innings_runs']:
                batting_stats['highest_score'] = int(highest_1st['first_innings_runs'])
                batting_stats['highest_score_team'] = str(highest_1st['team1'])
                batting_stats['highest_score_season'] = int(highest_1st['season'])
            else:
                batting_stats['highest_score'] = int(highest_2nd['second_innings_runs'])
                batting_stats['highest_score_team'] = str(highest_2nd['team2'])
                batting_stats['highest_score_season'] = int(highest_2nd['season'])
        
        # Load ball-by-ball data for boundaries and fielding stats
        try:
            ball_df = pd.read_csv('data/IPL.csv')
            venue_balls = ball_df[ball_df['venue'] == venue]
            
            if len(venue_balls) > 0:
                # Boundaries
                fours = len(venue_balls[venue_balls['runs_batter'] == 4])
                sixes = len(venue_balls[venue_balls['runs_batter'] == 6])
                
                batting_stats['total_fours'] = fours
                batting_stats['total_sixes'] = sixes
                batting_stats['avg_fours_per_match'] = round(fours / len(venue_matches), 1)
                batting_stats['avg_sixes_per_match'] = round(sixes / len(venue_matches), 1)
                
                # Fielding stats - catches and run-outs
                catches = len(venue_balls[venue_balls['wicket_kind'] == 'caught'])
                runouts = len(venue_balls[venue_balls['wicket_kind'] == 'run out'])
                
                batting_stats['total_catches'] = catches
                batting_stats['total_runouts'] = runouts
                batting_stats['catches_per_match'] = round(catches / len(venue_matches), 2)
                batting_stats['runouts_per_match'] = round(runouts / len(venue_matches), 2)
                batting_stats['fielding_rank'] = 0  # Will be calculated after all venues processed
            else:
                # Fallback if no ball-by-ball data
                batting_stats.update({
                    'total_fours': 0, 'total_sixes': 0,
                    'avg_fours_per_match': 0, 'avg_sixes_per_match': 0,
                    'total_catches': 0, 'total_runouts': 0,
                    'catches_per_match': 0, 'runouts_per_match': 0
                })
        except:
            # If IPL.csv not available, use fallback
            batting_stats.update({
                'total_fours': 0, 'total_sixes': 0,
                'avg_fours_per_match': 0, 'avg_sixes_per_match': 0,
                'total_catches': 0, 'total_runouts': 0,
                'catches_per_match': 0, 'runouts_per_match': 0
            })
        
        venue_data['batting_stats'] = batting_stats
        
        venue_analytics[venue] = venue_data
    
    # === OVERALL TOSS STATISTICS ===
    overall_toss_stats = {
        'total_matches': len(df),
        'toss_win_match_win': len(df[df['toss_winner'] == df['match_won_by']]),
        'total_bat_decisions': len(df[df['toss_decision'] == 'bat']),
        'total_field_decisions': len(df[df['toss_decision'] == 'field']),
    }
    
    total_with_toss = len(df[df['toss_winner'].notna() & df['match_won_by'].notna()])
    overall_toss_stats['toss_advantage_pct'] = round((overall_toss_stats['toss_win_match_win'] / total_with_toss * 100) if total_with_toss > 0 else 0, 1)
    overall_toss_stats['bat_decision_pct'] = round((overall_toss_stats['total_bat_decisions'] / (overall_toss_stats['total_bat_decisions'] + overall_toss_stats['total_field_decisions']) * 100), 1)
    
    # === CALCULATE FIELDING RANKS (by catches per match) ===
    # Only rank venues with at least 10 matches for statistical significance
    venues_with_catches = [(venue, data['batting_stats']['catches_per_match']) 
                           for venue, data in venue_analytics.items() 
                           if 'batting_stats' in data 
                           and data['batting_stats']['catches_per_match'] > 0
                           and data['total_matches'] >= 10]
    
    # Sort by catches per match descending
    venues_with_catches.sort(key=lambda x: x[1], reverse=True)
    
    # Assign ranks only to qualified venues
    for rank, (venue, _) in enumerate(venues_with_catches, 1):
        venue_analytics[venue]['batting_stats']['fielding_rank'] = rank
    
    # Mark non-qualified venues
    for venue, data in venue_analytics.items():
        if data['total_matches'] < 10 and 'batting_stats' in data:
            venue_analytics[venue]['batting_stats']['fielding_rank'] = None
    
    # Save
    output = {
        'venues': venue_analytics,
        'overall_toss_stats': overall_toss_stats
    }
    
    os.makedirs('webapp/static/data', exist_ok=True)
    with open('webapp/static/data/venue_analytics.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nGenerated analytics for {len(venue_analytics)} venues")
    print(f"Overall toss advantage: {overall_toss_stats['toss_advantage_pct']}%")
    
    # Print sample
    sample_venue = list(venue_analytics.keys())[0]
    print(f"\nSample for {sample_venue}:")
    print(f"  Matches: {venue_analytics[sample_venue]['total_matches']}")
    print(f"  Type: {venue_analytics[sample_venue]['venue_type']}")
    print(f"  Bat First Win %: {venue_analytics[sample_venue]['bat_first_win_pct']}%")

if __name__ == '__main__':
    generate_venue_analytics()
