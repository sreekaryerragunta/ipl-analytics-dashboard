import pandas as pd
import numpy as np

class EloTracker:
    def __init__(self, k_factor=30, base_rating=1500, home_advantage=0):
        self.k = k_factor
        self.ratings = {} # dict of team -> rating
        self.history = [] # list of dicts
        self.base_rating = base_rating
        self.home_advantage = home_advantage

    def get_rating(self, team):
        return self.ratings.get(team, self.base_rating)

    def calculate_expected_score(self, rating_a, rating_b):
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

    def update_ratings(self, team1, team2, winner, margin=None):
        r1 = self.get_rating(team1)
        r2 = self.get_rating(team2)
        
        # Outcome: 1 if team1 wins, 0 if team2 wins, 0.5 if tie
        if winner == team1:
            actual_score = 1
        elif winner == team2:
            actual_score = 0
        else:
            actual_score = 0.5 # Tie/No Result
            
        expected_score = self.calculate_expected_score(r1, r2)
        
        # Margin of victory multiplier (optional, can be added later)
        # For now, standard K-factor update
        
        new_r1 = r1 + self.k * (actual_score - expected_score)
        new_r2 = r2 + self.k * ((1 - actual_score) - (1 - expected_score))
        
        self.ratings[team1] = new_r1
        self.ratings[team2] = new_r2
        
        return new_r1, new_r2

    def process_matches(self, matches_df):
        """
        Process matches in chronological order.
        matches_df must have: date, team1, team2, winner
        """
        # Sort by date
        df = matches_df.sort_values('date').reset_index(drop=True)
        
        history_records = []
        
        for idx, row in df.iterrows():
            t1 = row['team1']
            t2 = row['team2']
            winner = row['match_won_by'] # or 'winner' column
            
            # Get pre-match ratings
            r1_pre = self.get_rating(t1)
            r2_pre = self.get_rating(t2)
            
            # Update
            # Handle Ties or No Result if needed
            # Assuming 'match_won_by' has team name or is NaN/Tie
            
            # Clean winner name to match team1/team2
            # (Assuming standardization happened before this)
            
            r1_post, r2_post = self.update_ratings(t1, t2, winner)
            
            history_records.append({
                'match_id': row.get('match_id'),
                'date': row['date'],
                'season': row.get('season'),
                'team1': t1,
                'team2': t2,
                'rating_team1_pre': r1_pre,
                'rating_team2_pre': r2_pre,
                'rating_team1_post': r1_post,
                'rating_team2_post': r2_post,
                'winner': winner,
                'win_prob_team1': self.calculate_expected_score(r1_pre, r2_pre)
            })
            
        return pd.DataFrame(history_records)

def run_elo_analysis(matches_path='../data/IPL_matches.csv'):
    df = pd.read_csv(matches_path)
    # Ensure standard names
    # (Assuming done in processing)
    
    tracker = EloTracker()
    history = tracker.process_matches(df)
    return history
