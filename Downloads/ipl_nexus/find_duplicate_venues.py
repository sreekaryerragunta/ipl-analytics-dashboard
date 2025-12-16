import pandas as pd

# Load data
df = pd.read_csv('data/IPL_matches.csv')

# Find potential duplicates
venues = df['venue'].unique()

print("=== POTENTIAL DUPLICATE VENUES ===\n")

# Group similar venue names
venue_groups = {}
for venue in sorted(venues):
    # Get base name (first few words)
    base = ' '.join(str(venue).split()[:4]) if pd.notna(venue) else ''
    if base:
        if base not in venue_groups:
            venue_groups[base] = []
        venue_groups[base].append(venue)

# Show groups with multiple entries
duplicates_found = False
for base, group in venue_groups.items():
    if len(group) > 1:
        duplicates_found = True
        print(f"\n{base}:")
        for v in group:
            count = len(df[df['venue'] == v])
            print(f"  - {v}: {count} matches")
        print(f"  TOTAL: {sum(len(df[df['venue'] == v]) for v in group)} matches")

if not duplicates_found:
    print("No obvious duplicates found based on first 4 words.")

# Check for renamed venues
print("\n\n=== CHECKING FOR KNOWN RENAMES ===")
known_renames = {
    'Feroz Shah Kotla': 'Arun Jaitley Stadium',
    'M.Chinnaswamy Stadium': 'M Chinnaswamy Stadium',
    'Punjab Cricket Association Stadium': 'Punjab Cricket Association IS Bindra Stadium'
}

for old, new in known_renames.items():
    old_matches = df[df['venue'].str.contains(old, na=False, case=False)]
    new_matches = df[df['venue'].str.contains(new, na=False, case=False)]
    if len(old_matches) > 0 or len(new_matches) > 0:
        print(f"\n{old} → {new}")
        print(f"  Old name matches: {len(old_matches)}")
        print(f"  New name matches: {len(new_matches)}")
