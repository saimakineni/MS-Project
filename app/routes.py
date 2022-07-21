from flask import render_template, url_for, request
from app import app
from src import utils


strtDate=''
endDate=''
@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')


# Get list of live tournaments
@app.route("/live_tournaments_list")
def live_tournaments_list():
    tournamentDic={}
    tournamentDic['list'] = utils.get_only_tournaments(live=True)
    tournamentDic['live'] = True
    return render_template("tournament_list.html", title = ' Live Tournaments', x=tournamentDic, matches_url = 'live_matches_list')

# Go to finished tourmantmes date picker page
@app.route("/finished_tournaments_date_picker")
def finished_tournaments_date_picker():
    return render_template("finished_tournments_DatePicker.html", title = 'Finished Tournaments')


# Get the finished matches between date range
@app.route("/finished_match_search", methods=['POST'])
def finished_match_search():
    if request.method == "POST":
        global strtDate
        global endDate
        strtDate = request.form.get('Start_Date')
        endDate = request.form.get('End_Date')
        tournamentDic={}
        tournamentDic['list'] = utils.get_finished_tournaments_list(strtDate, endDate)
        tournamentDic['live'] = False
        return render_template("tournament_list.html", title = 'Finished Tournaments', x = tournamentDic)


@app.route("/finished_tournaments_list")
def finished_tournaments_list():
    tournamentDic={}
    tournamentDic['list'] = utils.get_only_tournaments(live=False)
    tournamentDic['live'] = False
    return render_template("tournament_list.html", title = 'Finished Tournaments', x = tournamentDic)

# Get all the matches in the tournamet selected by the user
@app.route("/tournament_matches/<tournament>/<live>")
def tournament_matches(tournament, live):
    if live == 'True':
        tournaments = utils.get_tournaments(tournament, live, strtDate, endDate)
        return render_template("tournament.html", title = 'Live Tournaments', tournaments = tournaments, matches_url = 'live_matches')
    elif live == 'False':
        tournaments = utils.get_tournaments(tournament, live,strtDate,endDate)
        return render_template("tournament.html", title = 'Finished Tournaments', tournaments = tournaments, matches_url = 'finished_matches')

@app.route("/finished_tournaments")
def finished_tournaments():
    tournaments = utils.get_tournaments(live = False)
    return render_template("tournament.html", title = 'Finished Tournaments', tournaments = tournaments, matches_url = 'finished_matches')

# Route to match visualization page
@app.route("/matches/<filename>", methods = ['GET'])
def matches(filename):
    return render_template('match.html', filename = filename, title = 'Tennis Visualization')

# Matchlist of View more in live matches
@app.route("/live_matches/<tournament>")
def live_matches(tournament):
    matches_list = utils.get_matches(tournament, live = True)
    return render_template("matches_list.html", matches = matches_list, title = tournament)

# Match list of view more in finished matches
@app.route("/finished_matches/<tournament>/<live>")
def finished_matches(tournament, live):
    matches_list = utils.get_matches(tournament, strtDate,endDate,live = False)
    return render_template("matches_list.html", matches = matches_list, title = tournament)

# Route to the elastic search
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        field = request.form.get('fields')
        query = request.form.get('query')
        matches_list = utils.get_search_results(query, field)
        return render_template("search_results.html", matches = matches_list, title = query)
    return render_template("index.html")
