from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__, static_folder='static', template_folder='templates')

# Production configuration
app.config['ENV'] = os.getenv('FLASK_ENV', 'production')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False') == 'True'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/teams')
def teams():
    return render_template('teams.html')

@app.route('/venues')
def venues():
    return render_template('venues.html')

@app.route('/predict')
def predict():
    return render_template('predict.html')

@app.route('/archetypes')
def archetypes():
    return render_template('archetypes.html')

@app.route('/stats')
def stats():
    return render_template('stats.html')

@app.route('/player-matchup')
def player_matchup():
    return render_template('player_matchup.html')

@app.route('/data/<path:filename>')
def serve_data(filename):
    return send_from_directory('static/data', filename)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404  # Redirect to home on 404

@app.errorhandler(500)
def internal_error(error):
    return "Internal Server Error. Please try again later.", 500

if __name__ == '__main__':
    print("Starting IPL Analytics Dashboard...")
    # Use environment variables for production, fallback to dev settings
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'
    app.run(host='0.0.0.0', port=port, debug=debug)
