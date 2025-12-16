# IPL Analytics Report (2008-2025)

## 1. Executive Summary
This project analyzes 18 seasons of IPL data (2008-2025) to uncover trends in team dominance, venue characteristics, and match archetypes.
Key deliverables include:
- A comprehensive **Match Level Dataset** derived from ball-by-ball logs.
- An **Interactive Web Dashboard** featuring Elo ratings, venue insights, and a match predictor.
- **Match Archetype Clustering** identifying 4 distinct types of T20 contests.

## 2. Key Findings

### Team Dominance (Elo Ratings)
- **Chennai Super Kings** and **Mumbai Indians** show the highest sustained peak Elo ratings across multiple eras.
- New entrants like **Gujarat Titans** showed rapid rating ascension in their debut seasons.
- The Elo system effectively captures "Era dominance" better than raw title counts.

### Venue & Toss Effects
- **Chinnaswamy Stadium (Bangalore)** remains a graveyard for bowlers with high average scores and a significant "chasing bias".
- **Chepauk (Chennai)** favors teams batting first more than the league average, supporting "defendable" low totals.
- The "Win Toss, Win Match" probability fluctuates by season but generally hovers around **51-54%**, suggesting the toss is important but not determinant.

### Match Archetypes
Using K-Means clustering, we identified 4 match types:
1. **Defensive Battles**: Low scoring, bowler-dominated games.
2. **High Scoring Thrillers**: Both teams scoring 180+, often decided in the last over.
3. **One-Sided Chases**: Where the team batting second wins comfortably with wickets in hand.
4. **Average Contests**: Standard 150-160 run games with average margins.

## 3. Web Dashboard
The accompanying web application (`webapp/`) provides:
- **Team Analysis**: Interactive Elo history charts.
- **Venue Insights**: Sortable metrics for 30+ venues.
- **Predictor**: A Head-to-Head probability calculator based on historical matchups.

## 4. Usage
To run the dashboard:
1. Install requirements: `pip install -r requirements.txt`
2. Run data generation (if needed): `python src/generate_dashboard_data.py`
3. Launch app: `python webapp/app.py`
4. Open `http://127.0.0.1:5000` in your browser.
