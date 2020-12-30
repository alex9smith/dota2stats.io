from typing import Dict, Any, List
from .heroes import get_hero_from_id, get_hero_name, heroes, get_hero_id_from_name
from .teams import RADIANT, DIRE
from .stats import calculate_fantasy_points
import json
from json import JSONDecodeError

Summary = Dict[str, Any]


def get_empty_slots(value: Any=None) -> dict:
    """
    Helper function to get an dict pre-populated for each slot. Defaults to None values
    Returns
    -------
    {0: None, 1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None, 9: None}
    """
    return {0: value, 1: value, 2: value, 3: value, 4: value, 5: value, 6: value, 7: value, 8: value, 9: value}


# noinspection PyAttributeOutsideInit
class ReplaySummariser:
    def __init__(self, raw_replay: str) -> None:
        """
        Summarises Dota 2 replays.
        :param raw_replay: The raw parsed replay JSON.
        """
        self.raw_replay = raw_replay
        self.summarise()

    def parse_file(self) -> None:
        """
        Reads the supplied replay and divides it into the various categories expected
        to be necessary to pull data and avoids repeatedly looping over the entire
        replay.
        :return: None
        """
        self.rune_data = []
        self.epilogue_key = None
        self.death_data = []
        self.roshan_data = []
        self.interval_data = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: []}
        self.ten_min_data = {0: None, 1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None, 9: None}
        self.twenty_min_data = {0: None, 1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None,
                                9: None}
        self.combat_damage_data = []
        self.gold_data = []
        self.xp_data = []
        self.multikill_data = []
        self.firstblood_data = []
        self.buyback_data = []
        self.killstreak_data = []
        self.draft_info = []
        self.damage_data = []
        self.purchase_data = []
        self.aegis_data = []
        self.heal_data = []
        self.interval_zero = []
        self.item_data = []
        self.combat_log_modifiers = []
        for line in self.parsed_replay:
            if line['type'] == 'CHAT_MESSAGE_RUNE_PICKUP':
                self.rune_data.append(line)
            elif line['type'] == 'interval':
                self.interval_data[line['slot']].append(line)
                if line['time'] == 0:
                    self.interval_zero.append(line)
                elif line['time'] == 600:
                    self.ten_min_data[line['slot']] = line
                elif line['time'] == 1200:
                    self.twenty_min_data[line['slot']] = line
            elif line['type'] == 'draft_timings':
                self.draft_info.append(line)
            elif line['type'] == 'epilogue':
                self.epilogue_key = json.loads(line['key'])
            elif line['type'] == 'DOTA_COMBATLOG_DEATH':
                self.death_data.append(line)
            elif line['type'] == 'CHAT_MESSAGE_ROSHAN_KILL':
                self.roshan_data.append(line)
            elif line['type'] == 'CHAT_MESSAGE_COMBATLOG_DAMAGE':
                self.combat_damage_data.append(line)
            elif line['type'] == 'DOTA_COMBATLOG_GOLD':
                self.gold_data.append(line)
            elif line['type'] == 'DOTA_COMBATLOG_XP':
                self.xp_data.append(line)
            elif line['type'] == 'DOTA_COMBATLOG_MULTIKILL':
                self.multikill_data.append(line)
            elif line['type'] == 'CHAT_MESSAGE_FIRSTBLOOD':
                self.firstblood_data.append(line)
            elif line['type'] == 'DOTA_COMBATLOG_BUYBACK':
                self.buyback_data.append(line)
            elif line['type'] == 'DOTA_COMBATLOG_KILLSTREAK':
                self.killstreak_data.append(line)
            elif line['type'] == 'DOTA_COMBATLOG_DAMAGE':
                self.damage_data.append(line)
            elif line['type'] == 'DOTA_COMBATLOG_PURCHASE':
                self.purchase_data.append(line)
            elif line['type'] == 'CHAT_MESSAGE_AEGIS':
                self.aegis_data.append(line)
            elif line['type'] == 'DOTA_COMBATLOG_HEAL':
                self.heal_data.append(line)
            elif line['type'] == 'DOTA_COMBATLOG_PURCHASE':
                self.item_data.append(line)
            elif line['type'] == 'DOTA_COMBATLOG_MODIFIER_ADD':
                self.combat_log_modifiers.append(line)

    def analyse_draft(self) -> None:
        """
        Performs draft analysis and creates the radiant_picks, radiant_bans,
        dire_picks, dire_bans and first_pick members of the class.
        :return: None
        """
        rad_ban = []
        dire_ban = []
        rad_pick = []
        dire_pick = []
        rad_hero_ids = []
        dire_hero_ids = []
        self.team_bans = {2: dire_ban, 3: rad_ban}
        self.team_picks = {2: dire_pick, 3: rad_pick}
        self.team_ids = {2: dire_hero_ids, 3: rad_hero_ids}
        swap = {2: 3, 3: 2}

        # Find out who first pick is
        first_pick = self.draft_info[0]['draft_active_team']
        current = first_pick
        # Get the initial bans
        for i in range(0, 6):
            self.team_bans[current].append(get_hero_name(self.draft_info[i]['hero_id']))
            current = swap[current]
        # Get stage one picks
        self.team_picks[current].append(get_hero_name(self.draft_info[6]['hero_id']))
        self.team_ids[current].append(self.draft_info[6]['hero_id'])
        current = swap[current]
        self.team_picks[current].append(get_hero_name(self.draft_info[7]['hero_id']))
        self.team_ids[current].append(self.draft_info[7]['hero_id'])
        self.team_picks[current].append(get_hero_name(self.draft_info[8]['hero_id']))
        self.team_ids[current].append(self.draft_info[8]['hero_id'])
        current = swap[current]
        self.team_picks[current].append(get_hero_name(self.draft_info[9]['hero_id']))
        self.team_ids[current].append(self.draft_info[9]['hero_id'])
        # Second stage bans
        for i in range(10, 14):
            self.team_bans[current].append(get_hero_name(self.draft_info[i]['hero_id']))
            current = swap[current]
        # 2nd pick keeps first pick in 2nd phase picks
        current = swap[current]
        for i in range(14, 18):
            self.team_picks[current].append(get_hero_name(self.draft_info[i]['hero_id']))
            self.team_ids[current].append(self.draft_info[i]['hero_id'])
            current = swap[current]
        # Final bans
        self.team_bans[current].append(get_hero_name(self.draft_info[18]['hero_id']))
        current = swap[current]
        self.team_bans[current].append(get_hero_name(self.draft_info[19]['hero_id']))
        # Final picks
        self.team_picks[current].append(get_hero_name(self.draft_info[20]['hero_id']))
        self.team_ids[current].append(self.draft_info[20]['hero_id'])
        current = swap[current]
        self.team_picks[current].append(get_hero_name(self.draft_info[21]['hero_id']))
        self.team_ids[current].append(self.draft_info[21]['hero_id'])

        self.radiant_picks = {"pick_1": self.team_picks[RADIANT][0], "pick_2": self.team_picks[RADIANT][1],
                              "pick_3": self.team_picks[RADIANT][2], "pick_4": self.team_picks[RADIANT][3],
                              "pick_5": self.team_picks[RADIANT][4]}
        self.dire_picks = {"pick_1": self.team_picks[DIRE][0], "pick_2": self.team_picks[DIRE][1],
                           "pick_3": self.team_picks[DIRE][2], "pick_4": self.team_picks[DIRE][3],
                           "pick_5": self.team_picks[DIRE][4]}
        self.radiant_bans = {"ban_1": self.team_bans[RADIANT][0],
                             "ban_2": self.team_bans[RADIANT][1],
                             "ban_3": self.team_bans[RADIANT][2],
                             "ban_4": self.team_bans[RADIANT][3],
                             "ban_5": self.team_bans[RADIANT][4],
                             "ban_6": self.team_bans[RADIANT][5]}
        self.dire_bans = {"ban_1": self.team_bans[DIRE][0],
                          "ban_2": self.team_bans[DIRE][1],
                          "ban_3": self.team_bans[DIRE][2],
                          "ban_4": self.team_bans[DIRE][3],
                          "ban_5": self.team_bans[DIRE][4],
                          "ban_6": self.team_bans[DIRE][5]}
        if first_pick == RADIANT:
            self.first_pick = "Radiant"
        else:
            self.first_pick = "Dire"

    def get_hero_damage(self) -> None:
        """
        Computes hero damage
        :return: None
        """
        self.slot_to_damage = {0: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
                               1: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
                               2: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
                               3: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
                               4: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
                               5: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
                               6: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
                               7: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
                               8: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
                               9: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0}}

        unit_name_to_slot = {}
        for slot in self.slot_to_hero_id:
            unit_name_to_slot[get_hero_from_id(self.slot_to_hero_id[slot])] = slot

        for line in self.damage_data:
            attacker_slot = unit_name_to_slot.get(line["attackername"])
            target_slot = unit_name_to_slot.get(line["targetname"])
            if attacker_slot is not None and target_slot is not None and attacker_slot != target_slot and line[
                    "targetillusion"] is False:
                self.slot_to_damage[attacker_slot][target_slot] = self.slot_to_damage[attacker_slot][target_slot] + \
                                                                  line["value"]

    def get_player_names(self) -> None:
        """
        Reads the player names from the epilogue data and stores them in the
        slot_to_player_name dict. Slots 0-4 are radiant and 5-10 are dire.
        :return: None
        """
        self.slot_to_player_name = get_empty_slots()
        self.slot_to_steamid = get_empty_slots()
        for playerInfo in self.epilogue_key['gameInfo_']['dota_']['playerInfo_']:
            for slots in self.slot_to_hero_id:
                if self.slot_to_hero_id[slots] == \
                        heroes[bytes(playerInfo['heroName_']['bytes']).decode('utf-8')]['id']:
                    self.slot_to_steamid[slots] = playerInfo['steamid_']
                    try:
                        self.slot_to_player_name[slots] = bytes(playerInfo['playerName_']['bytes']).decode('utf-8')
                    except (UnicodeDecodeError, ValueError):
                        self.slot_to_player_name[slots] = "ERROR"

    def get_game_duration(self) -> None:
        """
        Retrieves game duration, stored in duration.
        :return None
        """
        self.duration = self.interval_data[0][-1]['time']

    def get_GPM_and_XPM_and_CS(self) -> None:
        """
        Computes GPM and XPM and net worth/xps/cs at each second.
        Stores in slot_to_GPM, slot_to_XPM, slot_to_NWS, slot_to_XPS,
        slot_to_LH, slot_to_deny, slot_to_LHS, slot_to_DENS
        :return None:
        """
        self.slot_to_GPM = get_empty_slots()
        self.slot_to_XPM = get_empty_slots()
        self.slot_to_LH = get_empty_slots()
        self.slot_to_deny = get_empty_slots()
        self.slot_to_NWS = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: []}
        self.slot_to_XPS = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: []}
        self.slot_to_LHS = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: []}
        self.slot_to_deny_at_second = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: []}
        for slot in self.slot_to_GPM:
            self.slot_to_GPM[slot] = self.interval_data[slot][-1]['gold'] / (self.duration / 60)
            self.slot_to_XPM[slot] = self.interval_data[slot][-1]['xp'] / (self.duration / 60)
            self.slot_to_LH[slot] = self.interval_data[slot][-1]['lh']
            self.slot_to_deny[slot] = self.interval_data[slot][-1]['denies']
            for x in range(0, self.duration + 1):
                self.slot_to_NWS[slot].append(self.interval_data[slot][x]['networth'])
                self.slot_to_XPS[slot].append(self.interval_data[slot][x]['xp'])
                self.slot_to_LHS[slot].append(self.interval_data[slot][x]['lh'])
                self.slot_to_deny_at_second[slot].append(self.interval_data[slot][x]['denies'])

    def get_slot_to_hero_id(self) -> None:
        """
        Works out which player slot is playing which hero and stores the ids in
        slot_to_hero_id dict. Slots 0-4 are radiant and 5-10 are dire.
        :return: None
        """
        self.slot_to_hero_id = get_empty_slots()
        for line in self.interval_zero:
            self.slot_to_hero_id[line['slot']] = line['hero_id']

        # Invert to also allow reverse lookups
        self.hero_id_to_slot = {v: k for k, v in self.slot_to_hero_id.items()}

    def get_hero_name_to_slot(self) -> None:
        """
        Healing data uses hero names, not slots or IDs so map hero names to
        Returns
        -------

        """

    def get_slot_to_game_end_stats(self) -> None:
        """
        Looks at the last entry in self.interval_data for each slot to get the
        stats per hero at the end of the game.
        """
        self.slot_to_game_end_stats = get_empty_slots()
        for slot in self.slot_to_game_end_stats:
            last_interval = self.interval_data[slot][-1]
            self.slot_to_game_end_stats[slot] = last_interval

    def get_lanes(self) -> None:
        """
        Computes the lanes each hero was in
        """
        self.slot_to_lane = get_empty_slots()
        top_min = [70, 150]
        top_max = [110, 180]
        mid_min = [110, 110]
        mid_max = [136, 136]
        bot_min = [150, 70]
        bot_max = [180, 110]
        # Find time zero in interval_data
        zero_time = 0
        for line in self.interval_data[0]:
            if line['time'] == 0:
                break
            zero_time = zero_time + 1

        for slot in self.slot_to_lane:
            lane_opts = {"top": 0, "mid": 0, "bot": 0, "other": 0}
            for x in range(zero_time, zero_time + 600):
                x_pos = self.interval_data[slot][x]['x']
                y_pos = self.interval_data[slot][x]['y']
                if top_min[0] < x_pos < top_max[0] and top_min[1] < y_pos < top_max[1]:
                    lane_opts["top"] = lane_opts["top"] + 1
                elif mid_min[0] < x_pos < mid_max[0] and mid_min[1] < y_pos < mid_max[1]:
                    lane_opts["mid"] = lane_opts["mid"] + 1
                elif bot_min[0] < x_pos < bot_max[0] and bot_min[1] < y_pos < bot_max[1]:
                    lane_opts["bot"] = lane_opts["bot"] + 1
                else:
                    lane_opts["other"] = lane_opts["other"] + 1
            self.slot_to_lane[slot] = max(lane_opts, key=lane_opts.get)

    def get_healing(self) -> None:
        """
        Calculates the total healing done by each player over the match
        Returns
        -------
        None. Sets a dict of slots to ally healing in `self.slot_to_healing`
        """
        self.slot_to_healing = get_empty_slots(value=0)
        for line in self.heal_data:
            if line["attackerhero"] and line["targethero"] and not line["attackerillusion"] and not line["targetillusion"]:
                healer_slot = self.hero_id_to_slot[get_hero_id_from_name(line["attackername"])]
                self.slot_to_healing[healer_slot] += line["value"]

    def get_stun_duration(self) -> None:
        """
        Calculates the total stun duration applied per slot to
        enemy heroes.
        Returns
        -------
        None. Sets a dict of slots to stun duration in `self.slot_to_stun_duration`
        """
        self.slot_to_stun_duration = get_empty_slots(value=0)
        hero_stuns = [
            line for line in self.combat_log_modifiers
            if line["attackerhero"] and line["targethero"]
               and not line["attackerillusion"] and not line["targetillusion"]
               and ("stun" in line["inflictor"] or "root" in line["inflictor"])
        ]
        for stun in hero_stuns:
            stunner_slot = self.hero_id_to_slot[get_hero_id_from_name(stun["attackername"])]
            self.slot_to_stun_duration[stunner_slot] += stun["stun_duration"]

    def _did_slot_get_first_blood(self, slot: int) -> bool:
        return self.firstblood_data[0]["player1"] == slot

    def summarise(self) -> None:
        """
        Reads the supplied replay and meta files and builds
        the hero and match summaries.
        :return: None
        """
        self.parsed_replay = []
        for line in self.raw_replay.split("\n"):
            try:
                if line.startswith("{"):
                    self.parsed_replay.append(json.loads(line))
            except JSONDecodeError:
                pass

        # Some parsing stuff here
        self.parse_file()
        self.analyse_draft()
        self.get_slot_to_hero_id()
        self.get_player_names()
        self.get_game_duration()
        self.get_GPM_and_XPM_and_CS()
        self.get_slot_to_game_end_stats()
        self.get_hero_damage()
        self.get_lanes()
        self.get_healing()
        self.get_stun_duration()

        radiant_kills = 0
        dire_kills = 0
        for slot in range(0, 5):
            radiant_kills = radiant_kills + self.slot_to_game_end_stats[slot]["kills"]
        for slot in range(5, 10):
            dire_kills = dire_kills + self.slot_to_game_end_stats[slot]["kills"]

        self.match_summary = {
            "match_id": self.epilogue_key['gameInfo_']['dota_']['matchId_'],
            # This next line looks weird.
            # The teams in the gameWinner_ value are reversed.
            # We don't know why. Just go with it.
            "radiant_won": (self.epilogue_key['gameInfo_']['dota_']['gameWinner_'] == DIRE),
            "radiant_kills": radiant_kills,
            "dire_kills": dire_kills,
            "duration": self.duration,  # Time in seconds,
            "first_blood_time": 120,  # Time in seconds
            "first_blood_hero": "Hero name",
            "picks": {
                "radiant": {
                    **self.radiant_picks
                    # etc
                },
                "dire": {
                    **self.dire_picks
                }
            },
            "bans": {
                "radiant": {
                    **self.radiant_bans
                },
                "dire": {
                    **self.dire_bans
                }
            },
            "first_pick": self.first_pick
        }

        # A list of player summaries
        self.player_summaries = []
        for slot in self.slot_to_hero_id:
            if slot < 5:
                side = "Radiant"
                victor = self.match_summary["radiant_won"]
            else:
                side = "Dire"
                victor = not (self.match_summary["radiant_won"])

            gold = {}
            xp = {}
            lh = {}
            deny = {}
            for x in range(0, self.duration + 1):
                gold[x] = self.slot_to_NWS[slot]
                xp[x] = self.slot_to_XPS[slot]
                lh[x] = self.slot_to_LHS[slot]
                deny[x] = self.slot_to_deny_at_second[slot]
            my_team_lane_gold = 0
            enemy_team_lane_gold = 0
            team_slots = range(0, 5) if slot < 5 else range(5, 10)
            enemy_slots = range(5, 10) if slot < 5 else range(0, 5)
            my_lane = self.slot_to_lane[slot]
            for team in team_slots:
                if self.slot_to_lane[team] == my_lane:
                    my_team_lane_gold = my_team_lane_gold + self.ten_min_data[team]['gold']
            for enemy in enemy_slots:
                if self.slot_to_lane[enemy] == my_lane:
                    enemy_team_lane_gold = enemy_team_lane_gold + self.ten_min_data[enemy]['gold']

            lane_status = 'draw'
            if enemy_team_lane_gold < 0.8 * my_team_lane_gold:
                lane_status = 'win'
            elif my_team_lane_gold < 0.8 * enemy_team_lane_gold:
                lane_status = 'lose'

            self.player_summaries.append({
                "match_id": self.match_summary["match_id"],
                "steam_id": self.slot_to_steamid[slot],
                "hero": get_hero_name(self.slot_to_hero_id[slot]),
                "player": self.slot_to_player_name[slot],
                "side": side,
                "won": victor,
                "kills": self.slot_to_game_end_stats[slot]["kills"],
                "deaths": self.slot_to_game_end_stats[slot]["deaths"],
                "assists": self.slot_to_game_end_stats[slot]["assists"],
                "net_worth": self.slot_to_NWS[slot][-1],
                "level": self.slot_to_game_end_stats[slot]["level"],
                "gpm": self.slot_to_GPM[slot],
                "xpm": self.slot_to_XPM[slot],
                "last_hits": self.slot_to_LH[slot],
                "denies": self.slot_to_deny[slot],
                "first_blood": self._did_slot_get_first_blood(slot),
                "enemy_stun_time": 1,
                "healing": self.slot_to_healing[slot],
                "obs_placed": self.slot_to_game_end_stats[slot]["obs_placed"],
                "sentries_placed": self.slot_to_game_end_stats[slot]["sen_placed"],
                "towers_killed": self.slot_to_game_end_stats[slot]["towers_killed"],
                "rosh_kills": self.slot_to_game_end_stats[slot]["roshans_killed"],
                "lane": self.slot_to_lane[slot],
                "lane_status": lane_status,
                "damage": self.slot_to_damage[slot],

            })

        # Go over the player summaries again to calculate fantasy points
        for player in self.player_summaries:
            player["fantasy_points"] = calculate_fantasy_points(player)

    def fantasy_points(self) -> List[Summary]:
        """
        Get fantasy points per player
        Returns
        -------
        A list of player names and fantasy points
        """
        return [
            {
                "player": player["player"],
                "steam_id": player["steam_id"],
                "hero": player["hero"],
                "fantasy_points": player["fantasy_points"]
            }
            for player in self.player_summaries
        ]
