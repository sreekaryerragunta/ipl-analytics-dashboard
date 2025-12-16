import pandas as pd
df = pd.read_csv('data/IPL_matches.csv')
print('Season vs Date mapping:')
for season in sorted(df['season'].unique()):
    if pd.notna(season):
        dates = df[df['season']==season]['date']
        print(f'Season {int(season)}: {dates.min()} to {dates.max()}')
