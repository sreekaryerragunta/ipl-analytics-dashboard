import pandas as pd
df = pd.read_csv('data/IPL.csv', low_memory=False)
print('Original season labels and their date ranges:')
for season in sorted(df['season'].unique()):
    if pd.notna(season):
        dates = df[df['season']==season]['date']
        print(f'Original Season "{season}": {dates.min()} to {dates.max()}')
