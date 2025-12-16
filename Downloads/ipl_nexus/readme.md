# IPL Analytics Dashboard 🏏

A comprehensive IPL (Indian Premier League) cricket analytics dashboard covering seasons 2008-2025.

## Features

- **Dashboard Overview**: IPL statistics at a glance
- **Team Analysis**: Performance trends, venue statistics, season breakdowns
- **Venue & Toss Analytics**: Ground performance, toss impact analysis
- **Team Matchup Predictor**: Head-to-head predictions
- **Player Matchup**: Batter vs bowler analysis
- **Player Archetypes**: Batting and bowling style classifications
- **Stats & Records**: 30+ comprehensive statistical categories

## Live Demo

🌐 **[Visit IPL Analytics Dashboard](#)** _(Add your Render URL here after deployment)_

## Tech Stack

- **Backend**: Flask (Python)
- **Data Processing**: Pandas
- **Frontend**: HTML, CSS, JavaScript
- **Charts**: Chart.js
- **Deployment**: Render.com / Railway

## Local Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ipl_nexus.git
cd ipl_nexus
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python webapp/app.py
```

4. Open browser and visit: `http://localhost:5000`

## Data

The dashboard uses:
- **IPL_matches.csv**: Match-level data (2008-2025)
- **IPL.csv**: Ball-by-ball data (2008-2025)

Generated analytics files in `webapp/static/data/`:
- Team performance, analytics, and match histories
- Venue statistics and toss impact
- Player profiles and archetypes
- Comprehensive batting/bowling/fielding records

## Deployment

This app is configured for easy deployment to Render.com:

1. Push code to GitHub
2. Connect repository to Render
3. Render will automatically use:
   - `requirements.txt` for dependencies
   - `Procfile` for start command
   - Gunicorn as WSGI server

## Mobile Support

✅ Fully responsive design
✅ Touch-optimized controls
✅ Works on all screen sizes (320px - 2560px)

## License

MIT License - feel free to use for personal or educational purposes.

## Credits

Built with ❤️ using official IPL data
Data covers 17+ seasons of IPL cricket
