import pandas as pd
import numpy as np
import os

def load_data(data_path='../data/IPL_matches.csv'):
    """
    Load processed match-level dataset.
    If not found, tries to load original and process? No, assumes processing done.
    """
    if not os.path.exists(data_path):
        # Fallback to raw if processed doesn't exist, but warn
        raw_path = data_path.replace('_matches.csv', '.csv')
        if os.path.exists(raw_path):
            print(f"Processed file {data_path} not found. Loading raw {raw_path}...")
            return pd.read_csv(raw_path, low_memory=False)
        raise FileNotFoundError(f"Data file not found at {data_path}")
    
    df = pd.read_csv(data_path)
    
    # Ensure date is datetime
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        
    return df

def standardize_teams(df):
    """
    Standardize team names (e.g., 'Rising Pune Supergiant' variations).
    """
    team_mapping = {
        'Rising Pune Supergiant': 'Rising Pune Supergiants',
        'Pune Warriors': 'Pune Warriors India',
        'Delhi Daredevils': 'Delhi Capitals', # Optional: treat as same franchise? usually kept separate or mapped to latest
        # Add more as discovered during exploration
    }
    
    cols_to_map = ['team1', 'team2', 'toss_winner', 'winner']
    for col in cols_to_map:
        if col in df.columns:
            df[col] = df[col].replace(team_mapping)
            
    return df

def derive_metrics(df):
    """
    Derive basic match metrics if they don't exist.
    """
    # Logic to handle missing derived columns if dataset is "ball-by-ball" or "match-level"
    # Based on typical IPL datasets, it's usually match-level or ball-by-ball. 
    # If it's ball-by-ball, we need aggregation. 
    # Since I haven't inspected the file yet, I'll write a generic inspect function first in the notebook
    # and refine this. For now, basic placeholders.
    return df

def standardize_venues(df):
    """
    Standardize venue names to combine duplicates and handle renamed stadiums.
    Based on actual IPL venue history and renamings.
    """
    venue_mapping = {
        # MA Chidambaram Stadium variations (Chennai)
        'MA Chidambaram Stadium, Chepauk': 'MA Chidambaram Stadium',
        'MA Chidambaram Stadium, Chepauk, Chennai': 'MA Chidambaram Stadium',
        'M.A. Chidambaram Stadium': 'MA Chidambaram Stadium',
        
        # Wankhede Stadium variations (Mumbai)
        'Wankhede Stadium, Mumbai': 'Wankhede Stadium',
        
        # M Chinnaswamy Stadium variations (Bengaluru)
        'M Chinnaswamy Stadium, Bengaluru': 'M Chinnaswamy Stadium',
        'M.Chinnaswamy Stadium': 'M Chinnaswamy Stadium',
        
        # Feroz Shah Kotla renamed to Arun Jaitley Stadium (Delhi)
        'Feroz Shah Kotla': 'Arun Jaitley Stadium',
        'Arun Jaitley Stadium, Delhi': 'Arun Jaitley Stadium',
        
        # Rajiv Gandhi International Stadium variations (Hyderabad)
        'Rajiv Gandhi International Stadium, Uppal': 'Rajiv Gandhi International Stadium',
        'Rajiv Gandhi International Stadium, Uppal, Hyderabad': 'Rajiv Gandhi International Stadium',
        
        # Eden Gardens variations (Kolkata)
        'Eden Gardens, Kolkata': 'Eden Gardens',
        
        # Sawai Mansingh Stadium variations (Jaipur)
        'Sawai Mansingh Stadium, Jaipur': 'Sawai Mansingh Stadium',
        
        # Punjab Cricket Association Stadium (Mohali) - Multiple variations
        'Punjab Cricket Association Stadium, Mohali': 'Punjab Cricket Association IS Bindra Stadium',
        'Punjab Cricket Association Stadium': 'Punjab Cricket Association IS Bindra Stadium',
        'Punjab Cricket Association IS Bindra Stadium, Mohali': 'Punjab Cricket Association IS Bindra Stadium',
        'Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh': 'Punjab Cricket Association IS Bindra Stadium',
        
        # Himachal Pradesh Cricket Association Stadium (Dharamsala)
        'Himachal Pradesh Cricket Association Stadium, Dharamsala': 'Himachal Pradesh Cricket Association Stadium',
        
        # Maharaja Yadavindra Singh International Cricket Stadium (Mullanpur/Mohali area)
        'Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur': 'Maharaja Yadavindra Singh International Cricket Stadium',
        'Maharaja Yadavindra Singh International Cricket Stadium, New Chandigarh': 'Maharaja Yadavindra Singh International Cricket Stadium',
        
        # Dr DY Patil Sports Academy variations (Mumbai)
        'Dr DY Patil Sports Academy, Mumbai': 'Dr DY Patil Sports Academy',
        
        # Brabourne Stadium (Mumbai)
        'Brabourne Stadium, Mumbai': 'Brabourne Stadium',
        
        # Maharashtra Cricket Association Stadium (Pune)
        'Maharashtra Cricket Association Stadium, Pune': 'Maharashtra Cricket Association Stadium',
        'MCA Stadium': 'Maharashtra Cricket Association Stadium',
        
        # Narendra Modi Stadium (Ahmedabad) - formerly Motera
        'Narendra Modi Stadium, Ahmedabad': 'Narendra Modi Stadium',
        'Sardar Patel Stadium, Motera': 'Narendra Modi Stadium',
        'Motera Stadium': 'Narendra Modi Stadium',
        
        # Ekana Cricket Stadium (Lucknow)
        'Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow': 'Ekana Cricket Stadium',
        'Ekana Cricket Stadium, Lucknow': 'Ekana Cricket Stadium',
        
        # Subrata Roy Sahara Stadium (Pune) - same as MCA Stadium
        'Subrata Roy Sahara Stadium': 'Maharashtra Cricket Association Stadium',
        
        # Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium (Visakhapatnam)
        'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam': 'ACA-VDCA Stadium',
        'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium': 'ACA-VDCA Stadium',
        
        # International stadiums
        'Dubai International Cricket Stadium': 'Dubai International Cricket Stadium',
        'Sheikh Zayed Stadium': 'Sheikh Zayed Stadium',
        'Sharjah Cricket Stadium': 'Sharjah Cricket Stadium',
        
        # South African venues
        'St George\'s Park': 'St George\'s Park',
        'Kingsmead': 'Kingsmead',
        'SuperSport Park': 'SuperSport Park',
        'New Wanderers Stadium': 'New Wanderers Stadium',
        'Newlands': 'Newlands',
        'OUTsurance Oval': 'OUTsurance Oval',
        'Buffalo Park': 'Buffalo Park',
    }
    
    if 'venue' in df.columns:
        df['venue'] = df['venue'].replace(venue_mapping)
    
    return df
