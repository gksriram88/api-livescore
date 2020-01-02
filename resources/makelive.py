from flask_restful import Resource, reqparse, request
from common.db import writeSQL, readSQL, readManySQL
import app, json
from common.util import default


class MakeLive(Resource):
    @app.jwt_required
    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('id', type=str, required=True, help="match id cannot be missing!", location='json')
        args = parser.parse_args()
        try:
            update_match= """
                UPDATE MATCH SET STATUS = 'LIVE' WHERE ID = %s
            """
            params = (args['id'],)
            update = writeSQL(update_match, params)
            if update:
                squad_key  = """
                    select match.team_a, match.team_b, player.id, player.name, player.first_name, player.last_name, player.batting_style, teamsquad.team_id, teamsquad.selected, teamsquad."position" from match
                    join squad on squad.id = match.squad_id
                    join teamsquad on teamsquad.t_id_1 = squad.team_squad_1 or teamsquad.t_id_2 = squad.team_squad_2
                    join player on player.id = teamsquad.player_id
                    where match.id= %s and (teamsquad.selected = true or teamsquad.selected = false)
                    GROUP BY teamsquad.team_id, player.id, player.name, teamsquad.team_id, teamsquad."position", match.team_a, match.team_b, teamsquad.selected
                    order by teamsquad."position" asc
                """
                params_key = (args['id'],)
                squad_players = readManySQL(squad_key, params_key)
                if(squad_players):
                    obj = {}
                    # innings 1 formation
                    obj["innings_1"] = {}
                    obj["innings_1"]["batting"] = {}
                    obj["innings_1"]["yetToBat"] = []
                    for player in squad_players:
                        if(player['team_id'] == player['team_a'] and player['selected']):
                            unq_name = str(player['id'])+"_pname"
                            obj["innings_1"]["batting"][unq_name] = {
                                                                    "id":player['id'],
                                                                    "name":player['name'],
                                                                    "first_name":player['first_name'],
                                                                    "last_name":player['last_name'],
                                                                    "batting_style": player['batting_style'],
                                                                    "status":"",
                                                                    "run":0,
                                                                    "balls":0,
                                                                    "four":0,
                                                                    "six":0,
                                                                    "strikeRate":0
                                                                }
                            obj["innings_1"]["totalRuns"] = 0
                            obj["innings_1"]["totalWickets"] = 0
                            obj["innings_1"]["totalOvers"] = 0
                            obj["innings_1"]["extras"] = {  
                                "byes":0,
                                "legByes":0,
                                "wide":0,
                                "noBall":0,
                                "pnlt":0
                            }
                            obj["innings_1"]["yetToBat"].append(player['name'])
                            obj["innings_1"]["fallOfWickets"] = []
                            obj["innings_1"]["Bowling"] = {}
                    # innings 2 formation
                    obj["innings_2"] = {}
                    obj["innings_2"]["batting"] = {}
                    obj["innings_2"]["yetToBat"] = []
                    for player in squad_players:
                        if(player['team_id'] == player['team_b'] and player['selected']):
                            unq_name = str(player['id'])+"_pname"
                            obj["innings_2"]["batting"][unq_name] = {
                                                                    "id":player['id'],
                                                                    "name":player['name'],
                                                                    "first_name":player['first_name'],
                                                                    "last_name":player['last_name'],
                                                                    "batting_style": player['batting_style'],
                                                                    "status":"",
                                                                    "run":0,
                                                                    "balls":0,
                                                                    "four":0,
                                                                    "six":0,
                                                                    "strikeRate":0
                                                                }
                            obj["innings_2"]["totalRuns"] = 0
                            obj["innings_2"]["totalWickets"] = 0
                            obj["innings_2"]["totalOvers"] = 0
                            obj["innings_2"]["extras"] = {  
                                "byes":0,
                                "legByes":0,
                                "wide":0,
                                "noBall":0,
                                "pnlt":0
                            }
                            obj["innings_2"]["yetToBat"].append(player['name'])
                            obj["innings_2"]["fallOfWickets"] = []
                            obj["innings_2"]["Bowling"] = {}
                    val = json.dumps(obj)
                    key = "fullscorecard:"+str(args['id'])
                    return_key = app.redis.set(key, val)
                    if return_key:
                        return { 'success': True }, 200
                    else:
                        return {'success': False, 'message': "SERVER/DB error" }, 500
            else:
                return {'success': False, 'message': 'no match found' }, 404
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500
    