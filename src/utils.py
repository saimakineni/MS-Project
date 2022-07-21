import pandas as pd

from datetime import datetime, timedelta
from collections import OrderedDict
from .db import db
from src import es
import json

def create_database():
    """
    Initialize a database and create the table if not present and return True
    """
    global conn
    conn = db('./data/db/matches.db')
    conn.create_table(create_match_sql())

def create_match_sql():
    return """CREATE TABLE IF NOT EXISTS matches (
                Tournament text NOT NULL,
                Date text NOT NULL,
                Round text NOT NULL,
                Player_1 text NOT NULL,
                Player_2 text NOT NULL,
                file_name text NOT NULL,
                index_date text NOT NULL,
                won text NOT NULL,
                result text NOT NULL,
                status text NOT NULL,
                url text
            );"""

def tournament_sql():
    return "SELECT * FROM matches WHERE status=?"
def finished_tournament_date_sql():
    return "SELECT Tournament FROM matches WHERE index_date BETWEEN ? AND ?"

def finished_tournaments_sql():
    return "SELECT * FROM matches WHERE status=? AND index_date BETWEEN ? AND ?"

def matches_sql():
    return "SELECT * FROM matches WHERE Tournament=? AND status=?"
def get_past_date(days = 0):
    format = '%Y-%m-%d'
    start = datetime.today() - timedelta(days = days)
    return datetime.strptime(start.strftime(format), format)

def get_matches_list(df, size = True):
    length = df.shape[0]
    if size and length > 5:
        df = df.iloc[:5]
    results = df.to_dict('records', into=OrderedDict)
    if size:
        results.append(length)
    return results

#Written by Sainadh to get tournment List
def get_only_tournaments(live):
    create_database()
    if live:
        tournaments = conn.select_data(tournament_sql(), ('live',))
    tournaments = pd.DataFrame(tournaments, columns = ['Tournament','Date','Round','Player_1','Player_2','file_name','index_date','won','result','status','url'])
    tourn_list = tournaments['Tournament'].value_counts().index.to_list()
    conn.close()
    return tourn_list

def get_finished_tournaments_list(strtDate, endDate):
    create_database()
    tournaments1 = conn.select_data(finished_tournament_date_sql(),(strtDate,endDate,))
    tournaments1 = pd.DataFrame(tournaments1, columns = ['Tournament'])
    tourn_list = tournaments1['Tournament'].value_counts().index.to_list()
    
    conn.close()
    return tourn_list


def get_tournaments(t,live,strtDate,endDate):
    results = dict()
    create_database()
    if live=='True':
        tournaments = conn.select_data(tournament_sql(), ('live',))
    elif live=="False":
        tournaments = conn.select_data(finished_tournaments_sql(), ('finished',strtDate,endDate))
    tournaments = pd.DataFrame(tournaments, columns = ['Tournament','Date','Round','Player_1','Player_2','file_name','index_date','won','result','status','url'])
    results[t] = get_matches_list(tournaments[tournaments['Tournament'] == t])
    conn.close()
    return results
    
def get_matches(tournament, strtDate, endDate, live, **kwargs):
    print("in getmatches date: ",strtDate,'+',endDate)
    results = dict()
    create_database()
    if live:
        tournaments = conn.select_data(matches_sql(), (tournament, 'live'))
    elif not live:
        tournaments = conn.select_data(finished_tournaments_sql(), ('finished',strtDate,endDate))
    tournaments = pd.DataFrame(tournaments, columns = ['Tournament','Date','Round','Player_1','Player_2','file_name','index_date','won','result','status','url'])
    results[tournament] = get_matches_list(tournaments[tournaments['Tournament'] == tournament], False)
    return results

def get_search_results(query, field):
    es_conn = es.connect_elasticsearch()
    if field == 'date':
        date_time_obj = datetime.strptime(query, '%Y-%m-%d')
        date_time_obj = date_time_obj.strftime("%d.%m.%y")
        query2 = str(date_time_obj)
    body = None
    matches = list()
    if field == 'round':
        body = { "query": {
            "multi_match" : {
                "query":    query, 
                "fields": [ "round" ] 
            }
            }
        }
    elif field == 'player':
        body = { "query": {
            "multi_match" : {
                "query":    query, 
                "fields": [ "Player_1", "Player_2" ] 
            }
            }
        }
    elif field == 'date':
        body = { "query": {
            "multi_match" : {
                "query":    query2, 
                "fields": [ "Date" ] 
            }
            }
        }
    elif field == 'tournament':
        body = { "query": {
            "multi_match" : {
                "query":    query, 
                "fields": [ "tournament" ] 
            }
            }
        }
    
    if body:
        results = es.search(es_conn, 'matches', body )
        for i in results['hits']['hits']:
            matches.append(i['_source'])
        es.close_connection(es_conn)
    to_return = {query: matches}
    return to_return