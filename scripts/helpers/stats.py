def calculate_fantasy_points(player) -> float:
    """
    Calculate the fantasy points this player earned from the formula

    Kill = 0.3
    Death = -0.3
    Assist = 0.15
    Last Hit = 0.003
    Gold per minute = 0.002
    EXP per minute = 0.002
    Seconds of enemy stuns = 0.07
    Every 1000 allied healing done = 0.4
    Tower Kill = 1
    Roshan Kill = 1
    First blood = 3
    https://dota2.gamepedia.com/Fantasy_Dota

    Parameters
    ----------
    player: Summary - a player summary

    Returns
    -------
    The fantasy points scored by this player
    """
    return (
        player["kills"]*0.3 - player["deaths"]*0.3 + player["assists"]*0.15 + player["last_hits"]*0.003
        + player["gpm"]*0.002 + player["xpm"]*0.002 + player["enemy_stun_time"]*0.07
        + (player["healing"]/1000)*0.4 + player["towers_killed"] + player["rosh_kills"]
        + (3 if player["first_blood"] else 0)
    )