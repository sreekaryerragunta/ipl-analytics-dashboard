import pandas as pd
import json
import os

def generate_advanced_team_analytics():
    """Generate comprehensive team analytics including venue performance, toss impact, batting first vs chasing"""
    
    def calculate_bat_chase_stats(matches, team):
        """Helper to calculate batting first vs chasing stats"""
        bat_first_matches = []
        chase_matches = []
        
        for _, row in matches.iterrows():
            if pd.isna(row['toss_decision']) or pd.isna(row['toss_winner']):
                continue
            
            if row['toss_decision'] == 'bat':
                batted_first = (row['toss_winner'] == team)
            else:
                batted_first = (row['toss_winner'] != team)
            
            if batted_first:
                bat_first_matches.append(row)
            else:
                chase_matches.append(row)
        
        bat_first_df = pd.DataFrame(bat_first_matches)
        chase_df = pd.DataFrame(chase_matches)
        
        bat_first_stats = {'played': 0, 'won': 0, 'lost': 0, 'win_rate': 0}
        chase_stats = {'played': 0, 'won': 0, 'lost': 0, 'win_rate': 0}
        
        if len(bat_first_df) > 0:
            bat_first_wins = len(bat_first_df[bat_first_df['match_won_by'] == team])
            bat_first_stats = {
                'played': len(bat_first_df),
                'won': bat_first_wins,
                'lost': len(bat_first_df) - bat_first_wins,
                'win_rate': round((bat_first_wins / len(bat_first_df) * 100), 1)
            }
        
        if len(chase_df) > 0:
            chase_wins = len(chase_df[chase_df['match_won_by'] == team])
            chase_stats = {
                'played': len(chase_df),
                'won': chase_wins,
                'lost': len(chase_df) - chase_wins,
                'win_rate': round((chase_wins / len(chase_df) * 100), 1)
            }
        
        return bat_first_stats, chase_stats
    
    def calculate_toss_impact(matches, team):
        """Helper to calculate toss impact"""
        toss_won = matches[matches['toss_winner'] == team]
        toss_lost = matches[matches['toss_winner'] != team]
        
        toss_won_matches = len(toss_won[toss_won['match_won_by'] == team])
        toss_lost_matches = len(toss_lost[toss_lost['match_won_by'] == team])
        
        return {
            'won_toss_won_match': toss_won_matches,
            'won_toss_total': len(toss_won),
            'lost_toss_won_match': toss_lost_matches,
            'lost_toss_total': len(toss_lost),
            'toss_win_advantage': round(
                ((toss_won_matches / len(toss_won) * 100) if len(toss_won) > 0 else 0) - 
                ((toss_lost_matches / len(toss_lost) * 100) if len(toss_lost) > 0 else 0), 
                1
            )
        }
    
    print("Loading data...")
    df = pd.read_csv('data/IPL_matches.csv')
    
    teams = set(df['team1'].dropna()).union(set(df['team2'].dropna()))
    
    advanced_data = {}
    
    for team in teams:
        print(f"Processing {team}...")
        
        # Get all matches for this team
        team_matches = df[(df['team1'] == team) | (df['team2'] == team)].copy()
        
        team_stats = {}
        
        # Get season ranges
        recent_seasons_3 = sorted(team_matches['season'].dropna().unique())[-3:]
        recent_seasons_5 = sorted(team_matches['season'].dropna().unique())[-5:]
        
        # ===== BATTING FIRST VS CHASING (ALL + FILTERED) =====
        bat_first_all, chase_all = calculate_bat_chase_stats(team_matches, team)
        team_stats['batting_first'] = bat_first_all
        team_stats['chasing'] = chase_all
        
        # Filtered versions
        last3_matches = team_matches[team_matches['season'].isin(recent_seasons_3)]
        last5_matches = team_matches[team_matches['season'].isin(recent_seasons_5)]
        
        bat_first_last3, chase_last3 = calculate_bat_chase_stats(last3_matches, team)
        bat_first_last5, chase_last5 = calculate_bat_chase_stats(last5_matches, team)
        
        team_stats['bat_chase_by_filter'] = {
            'all': {'batting_first': bat_first_all, 'chasing': chase_all},
            'last3': {'batting_first': bat_first_last3, 'chasing': chase_last3},
            'last5': {'batting_first': bat_first_last5, 'chasing': chase_last5}
        }
        
        # ===== TOSS IMPACT (ALL + FILTERED) =====
        toss_all = calculate_toss_impact(team_matches, team)
        team_stats['toss_impact'] = toss_all
        
        # Filtered versions
        toss_last3 = calculate_toss_impact(last3_matches, team)
        toss_last5 = calculate_toss_impact(last5_matches, team)
        
        team_stats['toss_impact_by_filter'] = {
            'all': toss_all,
            'last3': toss_last3,
            'last5': toss_last5
        }
        
        # ===== SEASON-BY-SEASON ANALYTICS =====
        # Generate batting first/chasing and toss impact for each season
        season_analytics = {}
        for season in sorted(team_matches['season'].dropna().unique()):
            season_matches = team_matches[team_matches['season'] == season]
            bat_first_season, chase_season = calculate_bat_chase_stats(season_matches, team)
            toss_season = calculate_toss_impact(season_matches, team)
            
            season_key = f'season_{int(season)}'
            season_analytics[season_key] = {
                'batting_first': bat_first_season,
                'chasing': chase_season,
                'toss_impact': toss_season
            }
        
        team_stats['season_analytics'] = season_analytics

        
        # ===== TOP VENUES =====
        venue_stats = []
        for venue, venue_group in team_matches.groupby('venue'):
            if pd.isna(venue):
                continue
            wins = len(venue_group[venue_group['match_won_by'] == team])
            total = len(venue_group)
            if total >= 10:  # Only include venues with at least 10 matches for meaningful stats
                venue_stats.append({
                    'venue': venue,
                    'played': total,
                   'won': wins,
                    'win_rate': round((wins / total * 100) if total > 0 else 0, 1)
                })
        
        # Sort by win rate, then by matches played
        venue_stats.sort(key=lambda x: (x['win_rate'], x['played']), reverse=True)
        team_stats['top_venues'] = venue_stats[:5]  # Top 5
        team_stats['worst_venues'] = sorted(venue_stats, key=lambda x: (x['win_rate'], -x['played']))[:5]
        
        # ===== SEASON-WISE VENUE STATS (for filtering) =====
        # Get last 3 and last 5 seasons
        recent_seasons_3 = sorted(team_matches['season'].dropna().unique())[-3:]
        recent_seasons_5 = sorted(team_matches['season'].dropna().unique())[-5:]
        
        # Venue stats for last 3 seasons
        last3_matches = team_matches[team_matches['season'].isin(recent_seasons_3)]
        venue_stats_last3 = []
        for venue, venue_group in last3_matches.groupby('venue'):
            if pd.isna(venue):
                continue
            wins = len(venue_group[venue_group['match_won_by'] == team])
            total = len(venue_group)
            if total >= 2:
                venue_stats_last3.append({
                    'venue': venue,
                    'played': total,
                    'won': wins,
                    'win_rate': round((wins / total * 100) if total > 0 else 0, 1)
                })
        venue_stats_last3.sort(key=lambda x: (x['win_rate'], x['played']), reverse=True)
        
        # Venue stats for last 5 seasons
        last5_matches = team_matches[team_matches['season'].isin(recent_seasons_5)]
        venue_stats_last5 = []
        for venue, venue_group in last5_matches.groupby('venue'):
            if pd.isna(venue):
                continue
            wins = len(venue_group[venue_group['match_won_by'] == team])
            total = len(venue_group)
            if total >= 2:
                venue_stats_last5.append({
                    'venue': venue,
                    'played': total,
                    'won': wins,
                    'win_rate': round((wins / total * 100) if total > 0 else 0, 1)
                })
        venue_stats_last5.sort(key=lambda x: (x['win_rate'], x['played']), reverse=True)
        
        team_stats['venue_stats_by_filter'] = {
            'all': {
                'top': venue_stats[:5],
                'worst': sorted(venue_stats, key=lambda x: (x['win_rate'], -x['played']))[:5]
            },
            'last3': {
                'top': venue_stats_last3[:5],
                'worst': sorted(venue_stats_last3, key=lambda x: (x['win_rate'], -x['played']))[:5]
            },
            'last5': {
                'top': venue_stats_last5[:5],
                'worst': sorted(venue_stats_last5, key=lambda x: (x['win_rate'], -x['played']))[:5]
            }
        }
        
        # ===== RECENT FORM (Last 10 matches) =====
        recent_matches = team_matches.sort_values('date', ascending=False).head(10)
        recent_wins = len(recent_matches[recent_matches['match_won_by'] == team])
        
        # Form string (e.g., "WWLWL")
        form = []
        for _, match in recent_matches.iterrows():
            if match['match_won_by'] == team:
                form.append('W')
            else:
                form.append('L')
        
        team_stats['recent_form'] = {
            'last_10_wins': recent_wins,
            'last_10_losses': 10 - recent_wins,
            'form_string': ''.join(form),
            'win_rate': round((recent_wins / 10 * 100), 1)
        }
        
        # ===== SEASON TRENDS (Recent seasons performance) =====
        season_trends = []
        seasons = sorted(team_matches['season'].dropna().unique())[-5:]  # Last 5 seasons
        
        for season in seasons:
            season_matches = team_matches[team_matches['season'] == season]
            wins = len(season_matches[season_matches['match_won_by'] == team])
            total = len(season_matches)
            season_trends.append({
                'season': int(season),
                'won': wins,
                'played': total,
                'win_rate': round((wins / total * 100) if total > 0 else 0, 1)
            })
        
        team_stats['season_trends'] = season_trends
        
        advanced_data[team] = team_stats
    
    # Save
    os.makedirs('webapp/static/data', exist_ok=True)
    with open('webapp/static/data/team_analytics.json', 'w') as f:
        json.dump(advanced_data, f, indent=2)
    
    print(f"\nGenerated advanced analytics for {len(advanced_data)} teams")
    
    # Print sample
    sample_team = list(advanced_data.keys())[0]
    print(f"\nSample for {sample_team}:")
    print(f"  Batting First: {advanced_data[sample_team]['batting_first']}")
    print(f"  Chasing: {advanced_data[sample_team]['chasing']}")
    print(f"  Recent Form: {advanced_data[sample_team]['recent_form']}")

if __name__ == '__main__':
    generate_advanced_team_analytics()
