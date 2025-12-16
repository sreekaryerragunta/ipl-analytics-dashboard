// Additional rendering functions for comprehensive stats
// This file contains rendering functions for all new stat categories
// Added to stats.html before closing script tag

// ========== SERIES & SEASONS ==========
function renderSeriesStats(container) {
    const season = currentSeason || Object.keys(statsData.series.series_stats).sort((a, b) => b - a)[0];
    const data = statsData.series.series_stats[season];
    
    container.innerHTML = `
        <div class="stats-header">
            <h2>Series Statistics - Season ${season}</h2>
            <p>Overview of the season</p>
        </div>
        <div class="top-cards">
            <div class="stat-card">
                <div class="stat-card-label">Total Matches</div>
                <div class="stat-card-value">${data.total_matches}</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-label">Teams</div>
                <div class="stat-card-value">${data.teams}</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-label">Winner</div>
                <div class="stat-card-value" style="font-size: 1.5rem;">${data.winner || 'TBD'}</div>
            </div>
        </div>
    `;
}

// ========== PLAYERS ==========
function renderPlayerProfiles(container) {
    const data = statsData.series.player_profiles || [];
    
    // Filter players with both batting and bowling stats
    const allRounders = data.filter(p => p.batting && p.bowling);
    const batsmen = data.filter(p => p.batting && !p.bowling).slice(0, 50);
    const bowlers = data.filter(p => p.bowling && !p.batting).slice(0, 50);
    
    container.innerHTML = `
        <div class="stats-header">
            <h2>Player Profiles</h2>
            <p>Comprehensive player statistics - ${data.length} total players</p>
        </div>
        <div style="margin-bottom: 1rem; color: #94A3B8;">
            <p>All-Rounders: ${allRounders.length} | Pure Batsmen: ${batsmen.length} | Pure Bowlers: ${bowlers.length}</p>
        </div>
    `;
}

// ========== TEAMS ==========
function renderTeamRecords(container) {
    const data = Object.values(statsData.team.team_records);
    const sorted = data.sort((a, b) => b.win_pct - a.win_pct);
    
    container.innerHTML = `
        <div class="stats-header">
            <h2>Team Records</h2>
            <p>Overall performance of all IPL teams</p>
        </div>
        <table class="stats-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Team</th>
                    <th class="text-center">Matches</th>
                    <th class="text-center">Wins</th>
                    <th class="text-center">Losses</th>
                    <th class="text-center">Win %</th>
                </tr>
            </thead>
            <tbody>
                ${sorted.map((team, idx) => `
                    <tr>
                        <td>
                            <span class="rank-badge rank-${idx < 3 ? idx + 1 : 'other'}">
                                ${idx + 1}
                            </span>
                        </td>
                        <td>${team.team}</td>
                        <td class="text-center">${team.matches}</td>
                        <td class="text-center stat-highlight">${team.wins}</td>
                        <td class="text-center">${team.losses}</td>
                        <td class="text-center">${team.win_pct}%</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// ========== GROUNDS ==========
function renderGroundRecords(container) {
    const data = statsData.ground.sort((a, b) => b.matches - a.matches);
    
    container.innerHTML = `
        <div class="stats-header">
            <h2>Ground Records</h2>
            <p>Statistics for all ${data.length} IPL venues</p>
        </div>
        <table class="stats-table">
            <thead>
                <tr>
                    <th>Venue</th>
                    <th class="text-center">Matches</th>
                    <th class="text-center">Avg 1st Innings</th>
                    <th class="text-center">Avg 2nd Innings</th>
                    <th class="text-center">Highest Total</th>
                    <th class="text-center">Lowest Total</th>
                </tr>
            </thead>
            <tbody>
                ${data.map(ground => `
                    <tr>
                        <td>${ground.venue}</td>
                        <td class="text-center">${ground.matches}</td>
                        <td class="text-center">${ground.avg_first_innings}</td>
                        <td class="text-center">${ground.avg_second_innings}</td>
                        <td class="text-center stat-highlight">${ground.highest_total}</td>
                        <td class="text-center">${ground.lowest_total}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// ========== MATCHES ==========
function renderTiedMatches(container) {
    const data = statsData.match.tied_matches;
    
    container.innerHTML = `
        <div class="stats-header">
            <h2>Tied Matches</h2>
            <p>All ${data.length} tied matches in IPL history</p>
        </div>
        <table class="stats-table">
            <thead>
                <tr>
                    <th>Season</th>
                    <th>Date</th>
                    <th>Team 1</th>
                    <th>Team 2</th>
                    <th class="text-center">Score</th>
                    <th>Venue</th>
                </tr>
            </thead>
            <tbody>
                ${data.map(match => `
                    <tr>
                        <td>${match.season}</td>
                        <td>${match.date}</td>
                        <td>${match.team1}</td>
                        <td>${match.team2}</td>
                        <td class="text-center stat-highlight">${match.score}</td>
                        <td>${match.venue}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function renderNarrowWins(container) {
    const data = statsData.match.narrow_wins;
    
    container.innerHTML = `
        <div class="stats-header">
            <h2>Narrow Wins</h2>
            <p>Closest finishes in IPL (< 5 runs or ≤ 2 wickets)</p>
        </div>
        <table class="stats-table">
            <thead>
                <tr>
                    <th>Season</th>
                    <th>Winner</th>
                    <th>vs</th>
                    <th class="text-center">Margin</th>
                    <th>Venue</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                ${data.map(match => `
                    <tr>
                        <td>${match.season}</td>
                        <td>${match.winner}</td>
                        <td>${match.team1 === match.winner ? match.team2 : match.team1}</td>
                        <td class="text-center stat-highlight">${match.margin}</td>
                        <td>${match.venue}</td>
                        <td>${match.date}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function renderWideWins(container) {
    const data = statsData.match.wide_wins;
    
    container.innerHTML = `
        <div class="stats-header">
            <h2>Wide Margin Wins</h2>
            <p>Most dominant victories (> 100 runs or ≥ 9 wickets)</p>
        </div>
        <table class="stats-table">
            <thead>
                <tr>
                    <th>Season</th>
                    <th>Winner</th>
                    <th>vs</th>
                    <th class="text-center">Margin</th>
                    <th>Venue</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                ${data.map(match => `
                    <tr>
                        <td>${match.season}</td>
                        <td>${match.winner}</td>
                        <td>${match.team1 === match.winner ? match.team2 : match.team1}</td>
                        <td class="text-center stat-highlight">${match.margin}</td>
                        <td>${match.venue}</td>
                        <td>${match.date}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function renderCloseChases(container) {
    const data = statsData.match.close_chases;
    
    container.innerHTML = `
        <div class="stats-header">
            <h2>Close Chases</h2>
            <p>Successful 150+ chases with ≤ 3 wickets remaining</p>
        </div>
        <table class="stats-table">
            <thead>
                <tr>
                    <th>Season</th>
                    <th>Chasing Team</th>
                    <th class="text-center">Target</th>
                    <th class="text-center">Wickets Left</th>
                    <th>Venue</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                ${data.map(match => `
                    <tr>
                        <td>${match.season}</td>
                        <td>${match.winner}</td>
                        <td class="text-center stat-highlight">${match.target}</td>
                        <td class="text-center">${match.wickets_left}</td>
                        <td>${match.venue}</td>
                        <td>${match.date}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// ========== SCORING RECORDS ==========
function renderHighestTotals(container) {
    const data = statsData.scoring.highest_totals.slice(0, 50);
    
    container.innerHTML = `
        <div class="stats-header">
            <h2>Highest Team Totals</h2>
            <p>Top 50 highest scores in IPL history</p>
        </div>
        <table class="stats-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Team</th>
                    <th class="text-center">Score</th>
                    <th>vs</th>
                    <th>Venue</th>
                    <th class="text-center">Season</th>
                    <th class="text-center">Won</th>
                </tr>
            </thead>
            <tbody>
                ${data.map((record, idx) => `
                    <tr>
                        <td>
                            <span class="rank-badge rank-${idx < 3 ? idx + 1 : 'other'}">
                                ${idx + 1}
                            </span>
                        </td>
                        <td>${record.team}</td>
                        <td class="text-center stat-highlight">${record.score}</td>
                        <td>${record.opponent}</td>
                        <td>${record.venue}</td>
                        <td class="text-center">${record.season}</td>
                        <td class="text-center">${record.won ? '✓' : '✗'}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function renderLowestTotals(container) {
    const data = statsData.scoring.lowest_totals.slice(0, 50);
    
    container.innerHTML = `
        <div class="stats-header">
            <h2>Lowest Team Totals</h2>
            <p>Top 50 lowest scores in IPL history</p>
        </div>
        <table class="stats-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Team</th>
                    <th class="text-center">Score</th>
                    <th>vs</th>
                    <th>Venue</th>
                    <th class="text-center">Season</th>
                </tr>
            </thead>
            <tbody>
                ${data.map((record, idx) => `
                    <tr>
                        <td>
                            <span class="rank-badge rank-${idx < 3 ? idx + 1 : 'other'}">
                                ${idx + 1}
                            </span>
                        </td>
                        <td>${record.team}</td>
                        <td class="text-center stat-highlight">${record.score}</td>
                        <td>${record.opponent}</td>
                        <td>${record.venue}</td>
                        <td class="text-center">${record.season}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function renderHighestAggregates(container) {
    const data = statsData.scoring.highest_aggregates.slice(0, 50);
    
    container.innerHTML = `
        <div class="stats-header">
            <h2>Highest Match Aggregates</h2>
            <p>Most runs scored in a match (both innings combined)</p>
        </div>
        <table class="stats-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th class="text-center">Total Runs</th>
                    <th>Team 1</th>
                    <th class="text-center">Score 1</th>
                    <th>Team 2</th>
                    <th class="text-center">Score 2</th>
                    <th>Venue</th>
                    <th class="text-center">Season</th>
                </tr>
            </thead>
            <tbody>
                ${data.map((record, idx) => `
                    <tr>
                        <td>
                            <span class="rank-badge rank-${idx < 3 ? idx + 1 : 'other'}">
                                ${idx + 1}
                            </span>
                        </td>
                        <td class="text-center stat-highlight">${record.total}</td>
                        <td>${record.team1}</td>
                        <td class="text-center">${record.score1}</td>
                        <td>${record.team2}</td>
                        <td class="text-center">${record.score2}</td>
                        <td>${record.venue}</td>
                        <td class="text-center">${record.season}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function renderHighestChases(container) {
    const data = statsData.scoring.highest_chases.slice(0, 50);
    
    container.innerHTML = `
        <div class="stats-header">
            <h2>Highest Successful Chases</h2>
            <p>Top 50 highest totals successfully chased down</p>
        </div>
        <table class="stats-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th class="text-center">Target</th>
                    <th>Chasing Team</th>
                    <th class="text-center">Wickets Left</th>
                    <th>vs</th>
                    <th>Venue</th>
                    <th class="text-center">Season</th>
                </tr>
            </thead>
            <tbody>
                ${data.map((record, idx) => `
                    <tr>
                        <td>
                            <span class="rank-badge rank-${idx < 3 ? idx + 1 : 'other'}">
                                ${idx + 1}
                            </span>
                        </td>
                        <td class="text-center stat-highlight">${record.target}</td>
                        <td>${record.chasing_team}</td>
                        <td class="text-center">${record.wickets_left}</td>
                        <td>${record.bowling_team}</td>
                        <td>${record.venue}</td>
                        <td class="text-center">${record.season}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// ========== PARTNERSHIPS ==========
function renderPartnerships(container, category) {
    let data, title, description;
    
    if (category === 'partnerships-50plus') {
        data = statsData.partnership.opening_partnerships_50plus;
        title = 'Opening Partnerships 50+';
        description = 'All opening partnerships of 50 runs or more';
    } else if (category === 'partnerships-100plus') {
        data = statsData.partnership.opening_partnerships_100plus;
        title = 'Opening Partnerships 100+';
        description = 'All opening partnerships of 100 runs or more';
    } else {
        data = statsData.partnership.top_opening_partnerships.slice(0, 50);
        title = 'Top Opening Partnerships';
        description = 'Top 50 opening partnerships in IPL history';
    }
    
    container.innerHTML = `
        <div class="stats-header">
            <h2>${title}</h2>
            <p>${description}</p>
        </div>
        <table class="stats-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th class="text-center">Runs</th>
                    <th>Batsmen</th>
                    <th>Team</th>
                    <th class="text-center">Season</th>
                </tr>
            </thead>
            <tbody>
                ${data.map((partnership, idx) => `
                    <tr>
                        <td>
                            <span class="rank-badge rank-${idx < 3 ? idx + 1 : 'other'}">
                                ${idx + 1}
                            </span>
                        </td>
                        <td class="text-center stat-highlight">${partnership.runs}</td>
                        <td>${partnership.batsmen.join(' & ')}</td>
                        <td>${partnership.team}</td>
                        <td class="text-center">${partnership.season}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// ========== ADDITIONAL BATTING FUNCTIONS ==========
function renderHighestAvg(container) {
    const data = statsData.batting.highest_avg.slice(0, 50);
    
    container.innerHTML = `
        <div class="stats-header">
            <h2>Highest Batting Averages</h2>
            <p>Top 50 batting averages (minimum 20 innings)</p>
        </div>
        <table class="stats-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Player</th>
                    <th class="text-center">Average</th>
                    <th class="text-center">Runs</th>
                    <th class="text-center">Matches</th>
                    <th class="text-center">Strike Rate</th>
                </tr>
            </thead>
            <tbody>
                ${data.map((player, idx) => `
                    <tr>
                        <td>
                            <span class="rank-badge rank-${idx < 3 ? idx + 1 : 'other'}">
                                ${idx + 1}
                            </span>
                        </td>
                        <td>${player.player}</td>
                        <td class="text-center stat-highlight">${player.avg}</td>
                        <td class="text-center">${player.runs}</td>
                        <td class="text-center">${player.matches}</td>
                        <td class="text-center">${player.sr}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function renderBestSR(container) {
    const data = statsData.batting.best_sr.slice(0, 50);
    
    container.innerHTML = `
        <div class="stats-header">
            <h2>Best Strike Rates</h2>
            <p>Top 50 strike rates (minimum 20 innings)</p>
        </div>
        <table class="stats-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Player</th>
                    <th class="text-center">Strike Rate</th>
                    <th class="text-center">Runs</th>
                    <th class="text-center">Balls</th>
                    <th class="text-center">Matches</th>
                </tr>
            </thead>
            <tbody>
                ${data.map((player, idx) => `
                    <tr>
                        <td>
                            <span class="rank-badge rank-${idx < 3 ? idx + 1 : 'other'}">
                                ${idx + 1}
                            </span>
                        </td>
                        <td>${player.player}</td>
                        <td class="text-center stat-highlight">${player.sr}</td>
                        <td class="text-center">${player.runs}</td>
                        <td class="text-center">${player.balls}</td>
                        <td class="text-center">${player.matches}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function renderMostFours(container) {
    const data = statsData.batting.most_fours.slice(0, 50);
    
    container.innerHTML = `
        <div class="stats-header">
            <h2>Most Fours</h2>
            <p>Top 50 players by number of boundaries</p>
        </div>
        <table class="stats-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Player</th>
                    <th class="text-center">Fours</th>
                    <th class="text-center">Runs</th>
                    <th class="text-center">Matches</th>
                </tr>
            </thead>
            <tbody>
                ${data.map((player, idx) => `
                    <tr>
                        <td>
                            <span class="rank-badge rank-${idx < 3 ? idx + 1 : 'other'}">
                                ${idx + 1}
                            </span>
                        </td>
                        <td>${player.player}</td>
                        <td class="text-center stat-highlight">${player.fours}</td>
                        <td class="text-center">${player.runs}</td>
                        <td class="text-center">${player.matches}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// ========== ADDITIONAL BOWLING FUNCTIONS ==========
function renderBowlingBestAvg(container) {
    const data = statsData.bowling.best_avg.slice(0, 50);
    
    container.innerHTML = `
        <div class="stats-header">
            <h2>Best Bowling Averages</h2>
            <p>Top 50 bowling averages (minimum 20 wickets)</p>
        </div>
        <table class="stats-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Player</th>
                    <th class="text-center">Average</th>
                    <th class="text-center">Wickets</th>
                    <th class="text-center">Runs</th>
                    <th class="text-center">Matches</th>
                </tr>
            </thead>
            <tbody>
                ${data.map((player, idx) => `
                    <tr>
                        <td>
                            <span class="rank-badge rank-${idx < 3 ? idx + 1 : 'other'}">
                                ${idx + 1}
                            </span>
                        </td>
                        <td>${player.player}</td>
                        <td class="text-center stat-highlight">${player.avg}</td>
                        <td class="text-center">${player.wickets}</td>
                        <td class="text-center">${player.runs}</td>
                        <td class="text-center">${player.matches}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function renderBowlingBestSR(container) {
    const data = statsData.bowling.best_sr.slice(0, 50);
    
    container.innerHTML = `
        <div class="stats-header">
            <h2>Best Bowling Strike Rates</h2>
            <p>Top 50 bowling strike rates (minimum 20 wickets)</p>
        </div>
        <table class="stats-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Player</th>
                    <th class="text-center">Strike Rate</th>
                    <th class="text-center">Wickets</th>
                    <th class="text-center">Average</th>
                    <th class="text-center">Matches</th>
                </tr>
            </thead>
            <tbody>
                ${data.map((player, idx) => `
                    <tr>
                        <td>
                            <span class="rank-badge rank-${idx < 3 ? idx + 1 : 'other'}">
                                ${idx + 1}
                            </span>
                        </td>
                        <td>${player.player}</td>
                        <td class="text-center stat-highlight">${player.sr}</td>
                        <td class="text-center">${player.wickets}</td>
                        <td class="text-center">${player.avg}</td>
                        <td class="text-center">${player.matches}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function renderMostEconomical(container) {
    const data = statsData.bowling.most_economical.slice(0, 50);
    
    container.innerHTML = `
        <div class="stats-header">
            <h2>Most Economical Spells</h2>
            <p>Top 50 economical bowling performances (minimum 4 overs)</p>
        </div>
        <table class="stats-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Player</th>
                    <th class="text-center">Economy</th>
                    <th class="text-center">Wickets</th>
                    <th class="text-center">Runs</th>
                    <th>vs</th>
                    <th class="text-center">Season</th>
                </tr>
            </thead>
            <tbody>
                ${data.map((player, idx) => `
                    <tr>
                        <td>
                            <span class="rank-badge rank-${idx < 3 ? idx + 1 : 'other'}">
                                ${idx + 1}
                            </span>
                        </td>
                        <td>${player.player}</td>
                        <td class="text-center stat-highlight">${player.economy}</td>
                        <td class="text-center">${player.wickets}</td>
                        <td class="text-center">${player.runs}</td>
                        <td>${player.team1} vs ${player.team2}</td>
                        <td class="text-center">${player.season}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// ========== ALL-ROUNDERS ==========
function renderTopAllRounders(container) {
    const data = statsData.fielding.top_allrounders.slice(0, 50);
    
    container.innerHTML = `
        <div class="stats-header">
            <h2>Top All-Rounders</h2>
            <p>Players with 500+ runs and 20+ wickets</p>
        </div>
        <table class="stats-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Player</th>
                    <th class="text-center">Runs</th>
                    <th class="text-center">Wickets</th>
                    <th class="text-center">Matches</th>
                    <th class="text-center">AR Index</th>
                </tr>
            </thead>
            <tbody>
                ${data.map((player, idx) => `
                    <tr>
                        <td>
                            <span class="rank-badge rank-${idx < 3 ? idx + 1 : 'other'}">
                                ${idx + 1}
                            </span>
                        </td>
                        <td>${player.player}</td>
                        <td class="text-center">${player.runs}</td>
                        <td class="text-center">${player.wickets}</td>
                        <td class="text-center">${player.matches}</td>
                        <td class="text-center stat-highlight">${Math.round(player.allrounder_index)}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}
