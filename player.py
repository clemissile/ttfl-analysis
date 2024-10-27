from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

# Define player ID and season
player = players.find_players_by_full_name('lebron james')
player_id = player[0]['id']
season = '2024-25'  # Update to the current season in 'YYYY-YY' format

# Fetch the game log for the player
gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=season)
gamelog_df = gamelog.get_data_frames()[0]

# Add custom metric calculation
gamelog_df['TTFL'] = (
    gamelog_df['PTS'] +  # Points
    gamelog_df['REB'] +  # Total Rebounds
    gamelog_df['AST'] +  # Assists
    gamelog_df['STL'] +  # Steals
    gamelog_df['BLK'] +  # Blocks
    gamelog_df['FGM'] +  # Field Goals Made
    gamelog_df['FG3M'] +  # 3-Point Field Goals Made
    gamelog_df['FTM']    # Free Throws Made
    -
    (gamelog_df['TOV'] +  # Turnovers
     (gamelog_df['FGA'] - gamelog_df['FGM']) +  # Field Goals Missed
     (gamelog_df['FG3A'] - gamelog_df['FG3M']) +  # 3-Point Field Goals Missed
     (gamelog_df['FTA'] - gamelog_df['FTM'])    # Free Throws Missed
    )
)

# Display the modified DataFrame with the new metric
print(gamelog_df[['TTFL']])