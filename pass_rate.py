player_dictionary = {}

def csv_prossr(csv_filename, season_year, injury_check):
    # injury_check = 0 default
    import csv
    import os.path
    import re
    
    # would be safer to have script determine csv's encoding
    # manually determined in linux by "file -bi <filename>"
    csv_file = open(csv_filename, 'rt', encoding='utf-8')
    csv_reader = csv.reader(csv_file)

    cumulative_completion = 0
    cumulative_attempts = 0
    cumulative_yards = 0
    cumulative_td = 0
    cumulative_int = 0
    cumulative_rating = 0

    for row in csv_reader:
        # csv file is currently formatted with the first line being "Name, Avg"
        # all subsequent elements are of that form
        # csv.reader formats each line ("row") as a list of strings
        # list indices:        
        # 0: name, 5: games played, 6: games started, 8: completed passes
        # 9: pass attempts, 11: yards, 12: touchdowns, 14: interceptions
        # 21: passer rating
        
        player_name = row[0]
        if player_name != "Rk":
            stripped_name = re.search(r'^[\w\s]+', player_name).group(0)
            games_played = float(row[5])
            games_started = float(row[6])
            completed_passes = float(row[8])
            pass_attempts = float(row[9])
            passing_yards = float(row[11])
            passing_tds = float(row[12])
            int_thrown = float(row[14])
            passer_rating = float(row[21])

            # include minimum games played/attempts according to pfrs below
            min_games = 16  # default min games
            if season_year == 1987:
                min_games = 15
            elif season_year == 1982:
                min_games = 9
            elif season_year in range(1961,1978):
                min_games = 14
            # endif
            
            # min qualifying attempts per game for every season:
            min_attempts = 14   # default min attempts per game played
            if season_year < 1976:
                min_games = 10
            elif season_year in range(1976,1978):
                min_games = 12
            # endif
            
            qualifying_passer = min_attempts * min_games
            
            # injured passers who were on pace to qualifying
            if injury_check:
                injury_check = pass_attempts / games_played * min_games
            
            # if pass_attempts >= qualifying_passer or injury_check >= qualifying_passer
            if pass_attempts >= qualifying_passer or injury_check > 0:
                player_dictionary[stripped_name] = {}
                current_player = player_dictionary[stripped_name]
                current_player['games_played'] = games_played
                current_player['games_started'] = games_started
                current_player['completed_passes'] = completed_passes
                current_player['pass_attempts'] = pass_attempts
                current_player['passing_yards'] = passing_yards
                current_player['passing_tds'] = passing_tds
                current_player['int_thrown'] = int_thrown
                current_player['passer_rating'] = passer_rating
                cumulative_completion += completed_passes
                cumulative_attempts += pass_attempts
                cumulative_yards += passing_yards
                cumulative_td += passing_tds
                cumulative_int += int_thrown
            # endif
    # end loop
    rating_a = (cumulative_completion / cumulative_attempts - 0.3) * 5
    rating_b = (cumulative_yards / cumulative_attempts - 3) * 0.25
    rating_c = cumulative_td / cumulative_attempts * 20
    rating_d = 2.375 - (cumulative_int / cumulative_attempts * 25)
    cumulative_rating = (rating_a + rating_b + rating_c + rating_d) / 6 * 100
    # for safety, close the file
    f1.close()
# end adding_ba_to_dict

import os.path
# 1966-2019 i.e. super bowl era
for season_year in range(2009,2019):
    # do something
    csv_filename = str(season_year) + ".csv"
    if os.path.isfile(csv_filename, season_year):
        csv_prossr(csv_filename, season_year, 0)
    else:
        print("file not found:",csv_filename)
        break
    # endif
# end loop