from pydfs_lineup_optimizer import get_optimizer, Site, Sport, CSVLineupExporter
import pandas as pd
import numpy as np


def get_daily_roster(csv_file):
    df = pd.read_csv(csv_file)
    return df


def create_predictions(predictions,
                       slate='\\\\home\\ubuntu\\Fantasy-Fire\\website\\optimizer\\Slates\\Main_Slate.csv'):
    pd.options.display.max_columns = 999
    pd.set_option('display.width', 1000)
    np.set_printoptions(threshold=10000000)
    df = pd.read_csv(slate)
    df2 = predictions
    result = df.merge(df2, left_on='Name', right_on='name', how='left')
    result = result.drop(
        columns=['AvgPointsPerGame', 'Name + ID', 'Game Info', 'Unnamed: 0', 'name'])
    result = result.rename(columns={'predicted': 'Predicted_FP'})
    result = result.fillna(0)
    result.to_csv("\\\\home\\ubuntu\\Fantasy-Fire\\website\\optimizer\\Predictions.csv")
    return result


if __name__ == '__main__':
    pd.options.display.max_columns = 999
    pd.set_option('display.width', 1000)
    np.set_printoptions(threshold=10000000)
    optimizer = get_optimizer(Site.DRAFTKINGS_CAPTAIN_MODE, Sport.BASKETBALL)
    # optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASKETBALL)
    df = pd.read_csv("Showdown 2.csv")
    df2 = pd.read_csv("prediction.csv")
    result = df.merge(df2, left_on='Name', right_on='name', how='left')
    result = result.drop(
        columns=['AvgPointsPerGame'])
    # 'Unnamed: 0_x', 'Unnamed: 0_x', 'Unnamed: 0_x.1', 'Unnamed: 0_x.1.1',
    # 'Unnamed: 0.1', 'name_x', 'Unnamed: 0_y', 'name_y', 'Unnamed: 0_y.1', 'name_x.1', 'Unnamed: 0_y.1.1',
    # 'name_y.1', 'Unnamed: 0_y', 'name'])
    # result = result.rename(columns={'predicted': 'AvgPointsPerGame'})
    result = result.fillna(0)
    result.to_csv("Predictions.csv")
    optimizer.load_players_from_csv('Predictions.csv')
    # drummond = optimizer.get_player_by_name('Drummond')
    # young = optimizer.get_player_by_name('Young')
    # curry = optimizer.get_player_by_name('Curry')
    # giannis = optimizer.get_player_by_name('Antetokounmpo')
    # gordon = optimizer.get_player_by_name('Gordon')
    # harden = optimizer.get_player_by_name('Harden')
    # reddish = optimizer.get_player_by_name('Cam Reddish')
    # beverley = optimizer.get_player_by_name('Beverley')
    # shamet = optimizer.get_player_by_name('Shamet')
    # draymond = optimizer.get_player_by_name('Green')
    # burks = optimizer.get_player_by_id('13630302')
    # robinson = optimizer.get_player_by_id('13630303')
    # chriss = optimizer.get_player_by_id('13630305')
    # print(player1)
    # player2 = optimizer.get_player_by_id('11653887')
    # print(player2)
    # order of priority goes player exposure, locked, and overall exposure
    # for lineup in optimizer.optimize(n=10, randomness=True):
    # optimizer.add_player_to_lineup(drummond)  # lock this player in lineup
    # optimizer.add_player_to_lineup(curry)  # lock this player in lineup
    # optimizer.add_player_to_lineup(gordon)
    # optimizer.add_player_to_lineup(robinson)
    # # optimizer.remove_player_from_lineup(player1)
    # optimizer.remove_player(burks)
    # optimizer.restore_player(player2)
    # player1.max_exposure = 0.5  # set max exposure
    # young.min_exposure = 0.3  # set min exposure
    # gordon.min_exposure = 0.6  # set min exposure
    # harden.min_exposure = 0.1
    # curry.min_exposure = 0.7
    # draymond.fppg = 100
    # chriss.min_exposure = 0.1
    # robinson.min_exposure = 0.3
    # reddish.fppg = 19
    # print(lineup)
    # print(lineup.players)  # list of players
    # print(lineup.fantasy_points_projection)
    # print(lineup.salary_costs)
    optimizer.set_deviation(0, 0.1)  # changing defaults of 0.06 and 0.12
    optimizer.set_min_salary_cap(49500)
    # optimizer.set_max_repeating_players(5) #restricts how many unique players each team must have
    # optimizer.set_team_stacking([3, 3]) #in this case, two teams must have at least 3 players present
    # optimizer.set_players_from_one_team({'GS': 2, 'LAC': 2})
    exporter = CSVLineupExporter(optimizer.optimize(37, randomness=True))
    exporter.export('lineups.csv')
