import os
import sys
sys.path.insert(0, os.path.abspath("C:\\Users\\Peter Argo\\Desktop\\INF 510\\Project\\Milestone 3\\python functions"))
global cur  
import sqlite3

# conn.close()
# Create the "connection".  team_stats.db is the file name that's created for our database
conn = sqlite3.connect('team_stats.db')
# Instantiate a "cursor" based on our connection.  We use this to send queries through

cur = conn.cursor()

# cur.execute('DROP TABLE IF EXISTS prim_ID ')
# cur.execute('CREATE TABLE prim_ID (team_id INTEGER, team_city TEXT, team_name TEXT, API_ID INTEGER)')

# Need to get the team_id as a primary key
cur.execute('DROP TABLE IF EXISTS Series ')
cur.execute('CREATE TABLE Series (postseason_series TEXT, winning_team INTEGER, losing_team INTEGER, year INTEGER, WTW INTEGER)')


cur.execute('DROP TABLE IF EXISTS Stats ')
cur.execute('CREATE TABLE Stats (team_id INTEGER, year INTEGER, OBP REAL, SLG REAL, HR REAL, WHIP REAL, ERA REAL, SO9 REAL)')

# Terminate the connection
# conn.close()


def baseball_ref_scraper(value): 
    """
    This function scraped baseball reference for the postseason series
    It takes that number of series that we want to analyze
    this funtion can take a maximum value of 190
    
    The outputs are:
    1. Array "year" that extraxts the year that each series was
    2. Array "winning_team-array" that extraxts the winner of each series
    3. Array "losing_team_array" that extracts the loser of each series
    4. Array "postseason_series" that extracts the title of the respective series (ex. "2019 ALDS")
    5. Array "more_wins" that returns a Boolean 1 or 0 depending on if the winning team had more wins than the losing team 
        more wins --> 1
        less wins --> 0
        ties --> 0
    6. value "cnt" which is the number of times the series winner and not winner had the same number of regular season wins
    """
    import requests
    from bs4 import BeautifulSoup
    r = requests.get("https://www.baseball-reference.com/postseason/")
    soup = BeautifulSoup(r.content, 'lxml')
    main_table = soup.findAll('table', {"id" : "postseason_series"})[0]
    main_body = main_table.findAll('tr')

    
    winning_team_array = []
    losing_team_array = []
    postseason_series = []
    more_wins = []
    year = []
    cnt = 0
    for i in range(value):
        postseason_series.append(str(main_body[i].find_all('th')[0].find_all('a')[0]).split('>')[1].split('<')[0])
        win_team_wins = str(main_body[i].find_all('td')[1].find_all('strong')[0].find_all('a', href=True)[0]).split('>')[1].split('(')[1].split('-')[0]
        loss_team_wins = str(main_body[i].find_all('td')[1].find_all('a')[1]).split('>')[1].split('(')[1].split('-')[0]
        wta = str(main_body[i].find_all('td')[1].find_all('strong')[0].find_all('a', href=True)[0]).split('>')[1].split(' ')
        lta = str(main_body[i].find_all('td')[1].find_all('a')[1]).split('>')[1].split(' ')
        if win_team_wins > loss_team_wins:
            more_wins.append(1)
        else:
            more_wins.append(0)
        if win_team_wins == loss_team_wins:
            cnt+=1

        if len(wta) > 4:
            if wta[1] == 'Blue':
                team = wta[1] + ' ' + wta[2]
            elif wta[1] == 'Red': #Account for 2 name teams
                team = wta[1] + ' ' + wta[2]

            else:
                team = wta[2]
        else:
            team = wta[1]
        if len(lta) > 4:
            if lta[1] == 'Blue': #Account for 2 name teams
                teamL = lta[1] + ' ' + lta[2]
            elif lta[1] == 'Red':
                 teamL = lta[1] + ' ' + lta[2]
            else:
                teamL = lta[2]
        else:
            teamL = lta[1]
        if team[-1] == '*': #Remove * That exists to show world series winner
            team = team[:-1]
        if teamL[-1] == '*': 
            teamL = teamL[:-1]
        if team == 'Sox':
            team = 'Red Sox'
        if teamL == 'Sox':
            teamL = 'Red Sox'

        winning_team_array.append(team)
        losing_team_array.append(teamL)
        year.append(int(postseason_series[i][0:4]))

    return(year, winning_team_array, losing_team_array, postseason_series, more_wins, cnt)

def create_db():    
    import sqlite3
    # conn.close()
    # Create the "connection".  team_stats.db is the file name that's created for our database
    conn = sqlite3.connect('team_stats.db')
    # Instantiate a "cursor" based on our connection.  We use this to send queries through

    cur = conn.cursor()

    # cur.execute('DROP TABLE IF EXISTS prim_ID ')
    # cur.execute('CREATE TABLE prim_ID (team_id INTEGER, team_city TEXT, team_name TEXT, API_ID INTEGER)')

    # Need to get the team_id as a primary key
    cur.execute('DROP TABLE IF EXISTS Series ')
    cur.execute('CREATE TABLE Series (postseason_series TEXT, winning_team INTEGER, losing_team INTEGER, year INTEGER, WTW INTEGER)')


    cur.execute('DROP TABLE IF EXISTS Stats ')
    cur.execute('CREATE TABLE Stats (team_id INTEGER, year INTEGER, OBP REAL, SLG REAL, HR REAL, WHIP REAL, ERA REAL, SO9 REAL)')

    # Terminate the connection
    # conn.close()

def read_from_db(val):
    """
    Function to query prim_ID table for foreign key
    input should be a string that matches either the team name or the city with a value in the prim_id table 
    outputs an integer value representing the foreign key for the respective table
    """
    # conn = sqlite3.connect('team_stats.db')
    # # Instantiate a "cursor" based on our connection.  We use this to send queries through
    # cur = conn.cursor()
    cmd_line = "SELECT team_id FROM prim_ID WHERE team_name = '%s' OR team_city = '%s'" % (val, val)
    cur.execute(cmd_line)
    try:
        ID = int(str(cur.fetchall()[0]).split('(')[1].split(',')[0])
    except:
        ID = 'Unknown'
    return ID

def reading(val):
    """
    Function to query prim_ID table for API ID's using the team ID as an input
    """
    
    cmd_line = "SELECT API_ID FROM prim_ID WHERE team_id = '%s'" % val
    cur.execute(cmd_line)
    try:
        ID = int(str(cur.fetchall()[0]).split('(')[1].split(',')[0])
    except:
        ID = 'Unknown'
    return ID



def playerID(response_roster):
    """
    The following function takes one roster from the MLB API roster_retrieval function as an input
    outputs an array of the player ID's for the input team
    
    """
    import re
    global player_id_array
    player_id_string_array = [m.start() for m in re.finditer('player_id', response_roster.text)]
    player_id_array = []
    for val in player_id_string_array:
        val = int(val)
        player_id = response_roster.text[val+12:val+18]
        player_id_array.append(player_id)
    #     print(player_id)
    return player_id_array

def roster_retrieval(year,team):
    """
    The function uses the year and the team ID input to scrape a roster from the MLB API
    The function outputs the roster information
    Use the year_and_win_and_lose array data
    """
    import requests
    import re
    response_roster = []
    url = "https://mlb-data.p.rapidapi.com/json/named.roster_team_alltime.bam"

    querystring = {"all_star_sw":"'N'","sort_order":"name_asc","end_season":str(year),"team_id":str(team),"start_season":str(year-1)}

    headers = {
        'x-rapidapi-host': "mlb-data.p.rapidapi.com",
        'x-rapidapi-key': "52d72158damshf14c292f35c4bdap1ec354jsnc179a7e5ec57"
        }
    response_roster.append(requests.request("GET", url, headers=headers, params=querystring)) #response_roster
    return response_roster

def get_player_name(val):
    """
    The function uses a player ID as an input
    Outputs the name of the player associated with that ID
    Iterate through the output of the player_ID function
    """
    import requests
    import re
    url_2 = "https://mlb-data.p.rapidapi.com/json/named.player_info.bam"
    querystring_2 = {"sport_code":"'mlb'","player_id":str(val)}
    
    headers = {
    'x-rapidapi-host': "mlb-data.p.rapidapi.com",
    'x-rapidapi-key': "52d72158damshf14c292f35c4bdap1ec354jsnc179a7e5ec57"
    }
    
    response_2 = requests.request("GET", url_2, headers=headers, params=querystring_2)
    return response_2

def get_plaer_stat(val):
    import requests
    import re
    """
    The function uses the player ID as an input
    Outputs the statistical profile for that player
    Iterate through the output of the player_ID function
    """
    url = "https://mlb-data.p.rapidapi.com/json/named.sport_hitting_tm.bam"
    querystring = {"season":str(year),"player_id":str(val),"league_list_id":"'mlb'","game_type":"'R'"}
    
    headers = {
    'x-rapidapi-host': "mlb-data.p.rapidapi.com",
    'x-rapidapi-key': "52d72158damshf14c292f35c4bdap1ec354jsnc179a7e5ec57"
    }
    
    response = requests.request("GET", url, headers=headers, params=querystring)
    return response