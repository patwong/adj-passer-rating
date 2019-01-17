player_dictionary = {}
career_dictionary = {}
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

    qb_list = []
    qb_injured_list = []
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
            if stripped_name.lower() == "nick foles":
                print("i'm here")
            # end test

            # if pass_attempts >= qualifying_passer or injury_check >= qualifying_passer
            if pass_attempts >= qualifying_passer or injury_check >= qualifying_passer:
                player_dictionary[stripped_name] = {}
                current_player = player_dictionary[stripped_name]
                completion_percentage = round(completed_passes / pass_attempts, 4) * 100
                td_percent = round(passing_tds / pass_attempts, 4) * 100
                int_percent = round(int_thrown / pass_attempts, 4) * 100
                current_player['games_played'] = games_played
                current_player['games_started'] = games_started
                current_player['completed_passes'] = completed_passes
                current_player['pass_attempts'] = pass_attempts
                current_player['passing_yards'] = passing_yards
                current_player['passing_tds'] = passing_tds
                current_player['int_thrown'] = int_thrown
                current_player['passer_rating'] = passer_rating
                current_player['completion_percentage'] = completion_percentage
                current_player['td_percent'] = td_percent
                current_player['int_percent'] = int_percent
                cumulative_completion += completed_passes
                cumulative_attempts += pass_attempts
                cumulative_yards += passing_yards
                cumulative_td += passing_tds
                cumulative_int += int_thrown
                # qb_temp = [stripped_name, games_played, games_started, completed_passes, pass_attempts,completion_percentage, passing_yards,passing_tds, td_percent, int_thrown, int_percent, passer_rating]
                if pass_attempts >= qualifying_passer:
                    qb_temp = [stripped_name, games_played, games_started, completed_passes, pass_attempts,
                               completion_percentage, passing_yards, passing_tds, td_percent, int_thrown, int_percent,
                               passer_rating]
                    qb_list.append(qb_temp)
                else:
                    qb_temp = [stripped_name + "*", games_played, games_started, completed_passes, pass_attempts,
                               completion_percentage, passing_yards, passing_tds, td_percent, int_thrown, int_percent,
                               passer_rating]
                    qb_injured_list.append(qb_temp)
            # endif
    # end loop
    rating_a = (cumulative_completion / cumulative_attempts - 0.3) * 5
    rating_b = (cumulative_yards / cumulative_attempts - 3) * 0.25
    rating_c = cumulative_td / cumulative_attempts * 20
    rating_d = 2.375 - (cumulative_int / cumulative_attempts * 25)
    cumulative_rating = (rating_a + rating_b + rating_c + rating_d) / 6 * 100
    cumulative_rating = cumulative_rating if cumulative_rating >= 0 else 0
    cumulative_rating = cumulative_rating if cumulative_rating <= 158.3 else 158.3
    cumulative_rating = "%.1f" % cumulative_rating
    print("league-wide passer rating is " + str(cumulative_rating))
    print("list of qualifying quarterbacks and their statistics, sorted by passer rating")
    # print("Name\t\tGames Played\t\tGames Started\t\tCompleted Passes\t\tPass Attempts\t\tYards\t\tTouchdowns\t\tInterceptions\t\tPasser Rating")
    qb_list_sorted = sorted(qb_list, key = lambda x: x[-1], reverse=True)
    qb_injured_list = sorted(qb_injured_list, key = lambda x: x[1], reverse=True)
    qb_csv = 'Player,Games Played,Games Started,Pass Completions,Pass Attempts,Comp%,Passing Yards,Touchdowns,TD%,Interceptions,Int%,Passer Rating\n'
    for qb in qb_list_sorted:
        output_string = ""
        csv_string = ""
        for qb_content in qb:
            output_string += str(qb_content) + '\t\t'
            csv_string += str(qb_content) + ','
        # end loop
        csv_string = csv_string[:-1] + '\n'
        qb_csv += csv_string
        output_string = output_string[:-2]
        # print(output_string)
    # end loop

    # outputting qbs who didn't qualify for the list
    for qb in qb_injured_list:
        csv_string = ""
        output_string = ""
        for qb_content in qb:
            output_string += str(qb_content) + '\t\t'
            csv_string += str(qb_content) + ','
        # end loop
        csv_string = csv_string[:-1] + '\n'
        qb_csv += csv_string
        output_string = output_string[:-2]
        print(output_string)
    # end loop
    csv_new = str(season_year) + "_sorted.csv"
    file1 = open(csv_new,'w')
    file1.write(qb_csv)
    file1.close()
# end adding_ba_to_dict

import os.path
# 1966-2019 i.e. super bowl era
csv_prossr('Data/2018.csv',2018,1)
# for season_year in range(2009,2019):
    # # do something
    # csv_filename = str(season_year) + ".csv"
    # if os.path.isfile(csv_filename, season_year):
        # csv_prossr(csv_filename, season_year, 0)
    # else:
        # print("file not found:",csv_filename)
        # break
    # # endif
# end loop