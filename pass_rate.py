player_dictionary = {}
season_dictionary = {}


def csv_prossr(csv_filename, season_year, injury_check):
    # injury_check = 0 default
    import csv
    import os.path
    import re
    # import scipy
    
    # would be safer to have script determine csv's encoding
    # manually determined in linux by "file -bi <filename>"
    csv_file = open(csv_filename, 'rt', encoding='utf-8')
    csv_reader = csv.reader(csv_file)

    cumulative_completion = 0
    cumulative_attempts = 0
    cumulative_yards = 0
    cumulative_td = 0
    cumulative_int = 0
    qb_qualified_list = []
    qb_unqualified_list = []
    season_dictionary[season_year] = {}
    current_season_stats = season_dictionary[season_year]
    for row in csv_reader:
        # csv file is currently formatted with the first line being "Name, Avg"
        # all subsequent elements are of that form
        # csv.reader formats each line ("row") as a list of strings
        # list indices:        
        # 0: name, 5: games played, 6: games started, 8: completed passes
        # 9: pass attempts, 11: yards, 12: touchdowns, 14: interceptions
        # 21: passer rating
        
        player_name = row[1]
        if player_name != "Player":
            stripped_name = re.search(r'^[\w\s\.\']+', player_name).group(0)
            games_played = int(row[5])
            games_started = int(row[6])
            completed_passes = int(row[8])
            pass_attempts = int(row[9])
            passing_yards = int(row[11])
            passing_tds = int(row[12])
            int_thrown = int(row[14])
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
                min_attempts = 10
            elif season_year in range(1976, 1978):
                min_attempts = 12
            # endif

            qualifying_passer = min_attempts * min_games

            # injured passers who were on pace to qualifying
            if injury_check:
                injury_check = pass_attempts / games_played * min_games
            # end if

            # debug check
            if stripped_name.lower() == "nick foles":
                print("i'm here")
            # end test

            # qualified: 0 -> not qualified, 1 -> qualified, 2 -> on pace for qualification
            qualified_check = 0
            if pass_attempts >= qualifying_passer:
                qualified_check = 1
            elif injury_check >= pass_attempts and injury_check >= qualifying_passer:
                qualified_check = 2
            else:
                qualified_check = 0
            # end if

            # check if the current player is in the dictionary
            if not(stripped_name in player_dictionary):
                player_dictionary[stripped_name] = {}
            # end if
            current_player = player_dictionary[stripped_name]
            current_player[season_year] = {}
            current_player_season = current_player[season_year]

            completion_percentage = round(completed_passes / pass_attempts, 4) * 100
            td_percent = round(passing_tds / pass_attempts, 4) * 100
            int_percent = round(int_thrown / pass_attempts, 4) * 100
            current_player_season['games_played'] = games_played
            current_player_season['games_started'] = games_started
            current_player_season['completed_passes'] = completed_passes
            current_player_season['pass_attempts'] = pass_attempts
            current_player_season['passing_yards'] = passing_yards
            current_player_season['passing_tds'] = passing_tds
            current_player_season['int_thrown'] = int_thrown
            current_player_season['passer_rating'] = passer_rating
            current_player_season['completion_percentage'] = completion_percentage
            current_player_season['td_percent'] = td_percent
            current_player_season['int_percent'] = int_percent
            current_player_season['qualified'] = qualified_check
            cumulative_completion += completed_passes
            cumulative_attempts += pass_attempts
            cumulative_yards += passing_yards
            cumulative_td += passing_tds
            cumulative_int += int_thrown

            # putting stats into the season dictionary
            current_season_stats[stripped_name] = current_player_season
            if pass_attempts >= qualifying_passer:
                qb_qualified_list.append(stripped_name)
            else:
                qb_unqualified_list.append(stripped_name)
    # end loop
    rating_a = (cumulative_completion / cumulative_attempts - 0.3) * 5
    rating_b = (cumulative_yards / cumulative_attempts - 3) * 0.25
    rating_c = cumulative_td / cumulative_attempts * 20
    rating_d = 2.375 - (cumulative_int / cumulative_attempts * 25)
    cumulative_rating = (rating_a + rating_b + rating_c + rating_d) / 6 * 100
    cumulative_rating = cumulative_rating if cumulative_rating >= 0 else 0
    cumulative_rating = cumulative_rating if cumulative_rating <= 158.3 else 158.3

    print("league-wide passer rating is " + str("%.1f" % cumulative_rating))
    print("list of qualifying quarterbacks and their statistics, sorted by passer rating")
    qb_list_sorted = sorted(qb_qualified_list, key = lambda x: x[-1], reverse=True)
    qb_unqualified_list = sorted(qb_unqualified_list, key = lambda x: x[1], reverse=True)
    qb_csv = 'Player,G,GS,Qualified,Cmp,Att,' \
                + 'Comp%,Yards,TD,TD%,Int,Int%,Passer Rating,PR+\n'
    for qb in qb_qualified_list:
        current_qb = season_dictionary[season_year][qb]
        current_qb['pr+'] = round(current_qb['passer_rating'] / cumulative_rating * 100, 1)
        # update player_dict
        csv_string = qb + "," \
                    + str(current_qb['games_played']) + ","     \
                    + str(current_qb['games_started']) + "," \
                    + str(current_qb['qualified']) + "," \
                    + str(current_qb['completed_passes']) + "," \
                    + str(current_qb['pass_attempts']) + "," \
                    + str(current_qb['completion_percentage']) + "," \
                    + str(current_qb['passing_yards']) + ","    \
                    + str(current_qb['passing_tds']) + "," \
                    + str(current_qb['td_percent']) + "," \
                    + str(current_qb['int_thrown']) + "," \
                    + str(current_qb['int_percent']) + "," \
                    + str(current_qb['passer_rating']) + ","    \
                    + str(current_qb['pr+'])
        csv_string += '\n'
        qb_csv += csv_string
    # end loop

    for qb in qb_unqualified_list:
        current_qb = season_dictionary[season_year][qb]
        current_qb['pr+'] = round(current_qb['passer_rating'] / cumulative_rating * 100, 1)
        # update player_dict
        csv_string = qb + "," \
                    + str(current_qb['games_played']) + ","     \
                    + str(current_qb['games_started']) + "," \
                    + str(current_qb['qualified']) + "," \
                    + str(current_qb['completed_passes']) + "," \
                    + str(current_qb['pass_attempts']) + "," \
                    + str(current_qb['completion_percentage']) + "," \
                    + str(current_qb['passing_yards']) + ","    \
                    + str(current_qb['passing_tds']) + "," \
                    + str(current_qb['td_percent']) + "," \
                    + str(current_qb['int_thrown']) + "," \
                    + str(current_qb['int_percent']) + "," \
                    + str(current_qb['passer_rating']) + ","    \
                    + str(current_qb['pr+'])
        csv_string += '\n'
        qb_csv += csv_string
    # end loop
    qb_csv += "NFL cumulative passer rating: " + ("%.1f" % cumulative_rating) + '\n'
    qb_csv += "qualified: 0 -> not qualified, 1 -> qualified, 2 -> on pace for qualification"
    csv_new = "Output/" + str(season_year) + "_sorted.csv"
    file1 = open(csv_new, 'w')
    file1.write(qb_csv)
    file1.close()
# end adding_ba_to_dict


# 1966-2019 i.e. super bowl era
csv_prossr('Data/2018.csv', 2018, 1)

# for season_year in range(2009,2019):
    # # do something
    # csv_filename = str(season_year) + ".csv"
    # if os.path.isfile(csv_filename, season_year):
        # csv_prossr(csv_filename, season_year, 1)
    # else:
        # print("file not found:",csv_filename)
        # break
    # # endif
# end loop