import os
import pickle

# pickle intiation
player_pickle = "Data/players.pickle"
season_pickle = "Data/seasons.pickle"
if os.path.isfile(player_pickle):
    with open(player_pickle, 'rb') as pickle_handle:
        player_dictionary = pickle.load(pickle_handle)
if os.path.isfile(season_pickle):
    with open(season_pickle, 'rb') as pickle_handle:
        season_dictionary = pickle.load(pickle_handle)
# end load
