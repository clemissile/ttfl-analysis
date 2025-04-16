import time
import random
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playergamelog, ScoreboardV2, commonteamroster
import pandas as pd
from datetime import datetime

# Set the current date in the format required by ScoreboardV2
today = datetime.today().strftime('%Y-%m-%d')

headers = {
    'Host': 'stats.nba.com',
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Origin': 'https://www.nba.com',
    'Referer': 'https://www.nba.com/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.5',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'Sec-GPC': '1'
}

# Fetch today's games using ScoreboardV2
games = ScoreboardV2(game_date=today, headers=headers)
games_data = games.get_data_frames()[1]

# Collect player IDs for players in today's games
player_ids = []
for _, game in games_data.iterrows():
    team_id = game['TEAM_ID']  # Get team ID from each row
    
    # Fetch team roster using commonteamroster endpoint
    roster = commonteamroster.CommonTeamRoster(team_id=team_id, season='2024-25', headers=headers)
    roster_data = roster.get_data_frames()[0]
    
    # Add each player's ID from the roster to player_ids list
    player_ids.extend(roster_data['PLAYER_ID'].tolist())

# Initialize list for storing players' TTFL averages
player_ttfl_averages = []

# Function to sleep and avoid throttling
def sleep_for_throttling():
    time.sleep(random.uniform(0.5, 1.0))  # Random sleep to avoid detection

# Loop through each player, calculate their TTFL average, and add to the list
for player_id in set(player_ids):  # Remove duplicates with set
    try:
        gamelog = playergamelog.PlayerGameLog(player_id=player_id, season='2024-25', headers=headers)
        gamelog_df = gamelog.get_data_frames()[0]

        if gamelog_df.empty:
            continue  # Skip if no game log data

        # Calculate TTFL for each game
        gamelog_df['TTFL'] = (
            gamelog_df['PTS'] +
            gamelog_df['REB'] +
            gamelog_df['AST'] +
            gamelog_df['STL'] +
            gamelog_df['BLK'] +
            gamelog_df['FGM'] +
            gamelog_df['FG3M'] +
            gamelog_df['FTM'] -
            (gamelog_df['TOV'] +
             (gamelog_df['FGA'] - gamelog_df['FGM']) +
             (gamelog_df['FG3A'] - gamelog_df['FG3M']) +
             (gamelog_df['FTA'] - gamelog_df['FTM']))
        )

        # Calculate TTFL average for the player
        ttfl_average = gamelog_df['TTFL'].mean()

        # Get player info
        player_info = players.find_player_by_id(player_id)
        player_name = player_info['full_name'] if player_info and 'full_name' in player_info else None

        # Append player name and TTFL average to the list
        player_ttfl_averages.append((player_name, ttfl_average))
        
        sleep_for_throttling()  # Sleep to avoid throttling after each request

    except Exception as e:
        print(f"Error processing player {player_id}: {e}")
        continue  # Skip the player if there's an error

# Sort by TTFL average in descending order and select the top 15
top_15_ttfl_players = sorted(player_ttfl_averages, key=lambda x: x[1], reverse=True)[:15]

# Display results with a nicely formatted ranking and emojis
print("🏆 Top 15 TTFL Players 🏆\n")
print(f"{'Rank':<5} {'Player':<25} {'TTFL Average':>12}")
print("━" * 45)

for rank, (player, avg_ttfl) in enumerate(top_15_ttfl_players, start=1):
    if rank == 1:
        rank_emoji = "🥇"
    elif rank == 2:
        rank_emoji = "🥈"
    elif rank == 3:
        rank_emoji = "🥉"
    else:
        rank_emoji = "⭐️" 

    print(f"{rank_emoji} {rank:<3} {player:<25} {avg_ttfl:>10.2f} pts")

print("\n🏀 Note: TTFL Average = Total TTFL Points per game")