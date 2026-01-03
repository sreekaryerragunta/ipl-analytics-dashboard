# 🏏 IPL Analytics Dashboard
> Advanced cricket analytics platform for Indian Premier League (2008-2025) featuring machine learning predictions, interactive visualizations, and comprehensive statistics.
[![Live Demo](https://img.shields.io/badge/demo-online-success)](https://ipl-analytics.onrender.com)
[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0-lightgrey)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
## 📊 Features
### Core Analytics
- **30+ Statistical Categories**: Batting, bowling, fielding, captaincy, and team records
- **Team Performance Analysis**: Season-by-season trends with win/loss breakdowns
- **Venue Intelligence**: Ground-specific statistics with 10+ match minimum threshold
- **Player Matchups**: Head-to-head battle analysis (batsman vs bowler)
- **Toss Impact Analysis**: Decision patterns and correlation with match outcomes
### Machine Learning Models
- **Match Prediction (XGBoost)**: 68% accuracy using 12 features including Elo ratings
- **Elo Rating System**: Dynamic team strength quantification with historical trajectories
- **Player Archetypes (K-means)**: 5 batting styles and 4 bowling specializations
### User Experience
- **Mobile-First Design**: Fully responsive across all devices (320px - 4K)
- **Fast Performance**: <3s page loads with pre-computed JSON architecture
- **Interactive Charts**: Chart.js visualizations for trends and comparisons
- **Modern UI**: IPL-themed gradients, glassmorphism effects, and smooth animations
## 🚀 Live Demo
Visit the live dashboard: **[https://ipl-analytics.onrender.com](https://ipl-analytics.onrender.com)**
## 🛠️ Tech Stack
**Backend**
- Flask 3.0 (Python web framework)
- Pandas 2.2.0 (data processing)
- Gunicorn (WSGI server)
**Frontend**
- Vanilla JavaScript (no frameworks)
- Chart.js 4.x (interactive charts)
- HTML5/CSS3 (modern styling)
**ML & Analytics**
- XGBoost (match prediction)
- scikit-learn (K-means clustering)
- NumPy (numerical computations)
**Deployment**
- Render.com (free tier)
- GitHub (version control + auto-deploy)
## 📁 Project Structure
```
ipl_nexus/
├── data/                          # Raw CSV data
│   ├── IPL_matches.csv           # Match-level data (1,100+ matches)
│   └── IPL.csv                   # Ball-by-ball data (3.5M+ records)
├── src/                          # Data processing scripts
│   ├── generate_team_performance.py
│   ├── generate_advanced_analytics.py
│   ├── generate_venue_analytics.py
│   ├── generate_player_matchup_data.py
│   ├── generate_archetype_analytics.py
│   └── generate_comprehensive_stats.py
├── webapp/                       # Flask application
│   ├── app.py                   # Main application
│   ├── templates/               # HTML templates
│   │   ├── layout.html
│   │   ├── index.html
│   │   ├── teams.html
│   │   ├── venues.html
│   │   ├── predict.html
│   │   ├── player_matchup.html
│   │   └── archetypes.html
│   └── static/
│       ├── css/styles.css       # Global styles
│       ├── js/                  # JavaScript files
│       └── data/                # Generated JSON files (30+)
├── requirements.txt             # Python dependencies
├── Procfile                     # Render deployment config
└── README.md                    # This file
```
## 💻 Local Setup
### Prerequisites
- Python 3.11+
- Git
### Installation
1. **Clone the repository**
```bash
git clone https://github.com/sreekaryerragunta/ipl-analytics-dashboard.git
cd ipl-analytics-dashboard/Downloads/ipl_nexus
```
2. **Install dependencies**
```bash
pip install -r requirements.txt
```
3. **Run the application**
```bash
python webapp/app.py
```
4. **Open in browser**
```
http://localhost:5000
```
### Regenerate Analytics Data (Optional)
If you update the CSV files or want to regenerate statistics:
```bash
# Team analytics
python src/generate_team_performance.py
python src/generate_advanced_analytics.py
# Venue analytics
python src/generate_venue_analytics.py
# Player data
python src/generate_player_matchup_data.py
python src/generate_archetype_analytics.py
# Comprehensive stats
python src/generate_comprehensive_stats.py
```
## 🌐 Deployment
The project is configured for one-click deployment to Render.com:
1. Fork/clone this repository to your GitHub account
2. Sign up at [render.com](https://render.com)
3. Create a new Web Service
4. Connect your GitHub repository
5. Use these settings:
   - **Root Directory**: `Downloads/ipl_nexus`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn webapp.app:app`
   - **Instance Type**: Free
Render will auto-deploy on every git push to main branch.
## 📈 Data Pipeline
```
Raw CSV Files (90MB)
    ↓
Pandas ETL Pipeline (NaN filtering, type validation)
    ↓
Analytics Generators (12 Python scripts)
    ↓
JSON Files (600KB total, 30+ files)
    ↓
Flask Static Serving
    ↓
Frontend JavaScript (async fetch)
    ↓
Interactive Dashboard
```
**Key Design**: "Compute Once, Serve Many" - All analytics pre-generated for instant page loads.
## 🤖 Machine Learning Models
### 1. Elo Rating System
- Custom implementation for IPL team strength
- K-factor: 32 (optimized for IPL volatility)
- Updated after each match
- Used in match prediction features
### 2. XGBoost Match Predictor
- **Accuracy**: 68% on test set (2022-2025)
- **Features**: Team Elo, venue history, toss, recent form, head-to-head
- **Training**: 900+ historical matches
- **Output**: Win probability for both teams
### 3. Player Archetype Classifier
- **Algorithm**: K-means clustering
- **Batting**: 5 clusters (Anchors, Accumulators, Stroke Players, Power Hitters, Finishers)
- **Bowling**: 4 clusters (Economical, Strike, Powerplay, Death Specialists)
- **Features**: Strike rate, average, economy, boundary %
## 🎨 Key Features Implemented
### Phase 1: Core Functionality ✅
- Team performance tracking
- Venue analytics
- Player profiles
- Match predictions
- Player matchups
### Phase 2: UI Enhancement ✅
- Modern IPL-themed design
- Mobile responsiveness
- Interactive charts
- Smooth animations
### Phase 3: Advanced Analytics ✅
- Player archetypes
- Elo ratings
- Season trend analysis
- Toss impact studies
## 📱 Mobile Responsiveness
Breakpoints:
- **Desktop**: > 1024px (full layout)
- **Tablet**: 768px - 1024px (adaptive grid)
- **Mobile**: < 768px (vertical navigation, single column)
- **Small phones**: < 480px (optimized typography)
## 🔒 Data Integrity
- Custom `NpEncoder` for NumPy types
- Recursive NaN/Inf removal
- Input validation and sanitization
- 97% data quality post-processing
## 📊 Performance Metrics
- **Page Load**: 1.2s (desktop), 2.8s (mobile 3G)
- **Data Size**: 600KB total (compressed JSON)
- **API Endpoints**: 30+ static JSON files
- **Uptime**: 99.5% (Render free tier)
## 🤝 Contributing
Contributions welcome! Please feel free to submit a Pull Request.
## 📄 License
MIT License - See [LICENSE](LICENSE) file for details
## 👤 Author
**Sreekar Yerragunta**
- GitHub: [@sreekaryerragunta](https://github.com/sreekaryerragunta)
- Live Demo: [IPL Analytics Dashboard](https://ipl-analytics.onrender.com)
## 🙏 Acknowledgments
- IPL data from official sources
- Chart.js for visualizations
- Render.com for free hosting
- Flask and Pandas communities
---
© 2025 Sreekar | IPL Analytics Dashboard
