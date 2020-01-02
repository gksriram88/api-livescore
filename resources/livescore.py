from flask_restful import Resource, reqparse
from common.db import writeSQL, readSQL
from common.util import default
import app, json


class LiveScore(Resource):
    @app.jwt_required
    def get(self, matchid):
        try:
            query_match= """
                SELECT SCORE_ID FROM MATCH WHERE ID = %s
                """
            params = (matchid,)
            row_score = readSQL(query_match, params)
            if row_score:
                query_score= """
                SELECT SCORECARD_ID FROM SCORE WHERE ID = %s
                """
                params = (row_score['score_id'],)
                row_scorecard_id = readSQL(query_score, params)
                if row_scorecard_id:
                    query_playerscorecard= """
                    SELECT * FROM PLAYERSCORECARD WHERE S_ID = %s ORDER BY ID desc limit 1
                    """
                    params = (row_scorecard_id['scorecard_id'],)
                    row_playerscorecard = readSQL(query_playerscorecard, params)
                    if row_playerscorecard:
                        row_card = {}
                        row_card = row_playerscorecard
                        get_curr_inngs = app.redis.get("match:"+str(matchid)+":innings")
                        if get_curr_inngs:
                            get_key = "livescorecard:"+str(matchid)+":current:"+str(get_curr_inngs)
                            if get_key:
                                val = json.loads(app.redis.get(get_key))
                                row_card['ballid'] = val['ball']
                                data = json.dumps({'success' : True, 'card': row_card}, default=default)
                                return json.loads(data), 200
                else:
                    return {'success': False}, 404
            else:
                return {'success': False}, 404        
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500
            
    @app.jwt_required
    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        #match info
        parser.add_argument('match_id', type=int, required=True, help="Id of the match cannot be missing!", location='json')
        
        #striker info
        parser.add_argument('striker_name', type=str, required=True, help="Striker name cannot be missing!", location='json')
        parser.add_argument('striker_first_name', type=str, required=True, help="Striker first name cannot be missing!", location='json')
        parser.add_argument('striker_last_name', type=str, required=True, help="Striker last name cannot be missing!", location='json')
        parser.add_argument('display_striker_name', type=str, required=True, help="Display Striker name cannot be missing!", location='json')
        parser.add_argument('striker', type=int, required=True, help="Striker cannot be missing!", location='json')
        parser.add_argument('striker_position', type=int, required=True, help="Striker position cannot be missing!", location='json')
        parser.add_argument('striker_run', type=int, required=True, help="Striker run cannot be missing!", location='json')
        parser.add_argument('striker_4', type=int, required=True, help="Striker 4's cannot be missing!", location='json')
        parser.add_argument('striker_6', type=int, required=True, help="Striker 6's cannot be missing!", location='json')
        parser.add_argument('striker_strikerate', type=float, required=True, help="Striker strike rate cannot be missing!", location='json')
        parser.add_argument('striker_balls', type=int, required=True, help="Striker balls cannot be missing!", location='json')
        parser.add_argument('striker_out_name', type=str,  location='json')
        parser.add_argument('striker_wicket_name', type=str, location='json')
        parser.add_argument('striker_out', type=int,  location='json')
        parser.add_argument('striker_batting_style', type=str, location='json')
        parser.add_argument('striker_wicket', type=int, location='json')

        #non striker info
        parser.add_argument('non_striker_name', type=str, required=True, help="Non Striker name cannot be missing!", location='json')
        parser.add_argument('non_striker_first_name', type=str, required=True, help="Non Striker first name cannot be missing!", location='json')
        parser.add_argument('non_striker_last_name', type=str, required=True, help="Non Striker last name cannot be missing!", location='json')
        parser.add_argument('display_non_striker_name', type=str, required=True, help="Display Non Striker name cannot be missing!", location='json')
        parser.add_argument('non_striker', type=int, required=True, help="Non striker cannot be missing!", location='json')
        parser.add_argument('non_striker_position', type=int, required=True, help="Non striker position cannot be missing!", location='json')
        parser.add_argument('non_striker_run', type=int, required=True, help="Non striker run cannot be missing!", location='json')
        parser.add_argument('non_striker_4', type=int, required=True, help="Non striker 4's cannot be missing!", location='json')
        parser.add_argument('non_striker_6', type=int, required=True, help="Non striker 6's cannot be missing!", location='json')
        parser.add_argument('non_striker_strikerate', type=float, required=True, help="Striker strike rate cannot be missing!", location='json')
        parser.add_argument('non_striker_balls', type=int, required=True, help="Non striker balls cannot be missing!", location='json')
        parser.add_argument('non_striker_out_name', type=str,  location='json')
        parser.add_argument('non_striker_wicket_name', type=str, location='json')
        parser.add_argument('non_striker_out', type=int,  location='json')
        parser.add_argument('non_striker_batting_style', type=str, location='json')
        parser.add_argument('non_striker_wicket', type=int, location='json')
        
        #bowler info
        parser.add_argument('cur_bowler_name', type=str, required=True, help="Current bowler name cannot be missing!", location='json')
        parser.add_argument('cur_bowler_first_name', type=str, required=True, help="Current bowler first name cannot be missing!", location='json')
        parser.add_argument('cur_bowler_last_name', type=str, required=True, help="Current bowler last name cannot be missing!", location='json')
        parser.add_argument('cur_bowler', type=int, required=True, help="Current bowler cannot be missing!", location='json')
        parser.add_argument('cur_bowler_over', type=float, required=True, help="Current bowler over cannot be missing!", location='json')
        parser.add_argument('cur_bowler_eco', type=float, required=True, help="Current bowler economy cannot be missing!", location='json')
        parser.add_argument('cur_bowler_mai', type=int, required=True, help="Current bowler maiden cannot be missing!", location='json')
        parser.add_argument('cur_bowler_wic', type=int, required=True, help="Current bowler wicket cannot be missing!", location='json')
        parser.add_argument('cur_bowler_spell', type=int, required=True, help="Current bowler spell cannot be missing!", location='json')
        parser.add_argument('cur_bowler_run', type=int, required=True, help="Current bowler run cannot be missing!", location='json')
        parser.add_argument('ballid', type=int, required=True, help="Ballid cannot be missing!", location='json')
        parser.add_argument('cur_bowler_bowling_cat', type=str, required=True, help="Current bowler bowling category first name cannot be missing!", location='json')

        #prv bowler info
        parser.add_argument('prv_bowler_name', type=str, required=True, help="Current bowler name cannot be missing!", location='json')
        parser.add_argument('prv_bowler', type=int, required=True, help="Previous bowler cannot be missing!", location='json')
        parser.add_argument('prv_bowler_first_name', type=str, required=True, help="Previous bowler first name cannot be missing!", location='json')
        parser.add_argument('prv_bowler_last_name', type=str, required=True, help="Previous bowler last name cannot be missing!", location='json')
        parser.add_argument('prv_bowler_over', type=float, required=True, help="Previous bowler over cannot be missing!", location='json')
        parser.add_argument('prv_bowler_eco', type=float, required=True, help="Previous bowler economy cannot be missing!", location='json')
        parser.add_argument('prv_bowler_mai', type=int, required=True, help="Previous bowler maiden cannot be missing!", location='json')
        parser.add_argument('prv_bowler_wic', type=int, required=True, help="Previous bowler wicket cannot be missing!", location='json')
        parser.add_argument('prv_bowler_spell', type=int, required=True, help="Previous bowler spell cannot be missing!", location='json')
        parser.add_argument('prv_bowler_run', type=int, required=True, help="Previous bowler run cannot be missing!", location='json')

        #field player info
        parser.add_argument('field_player_name', type=str, required=True, help="Field player name cannot be missing!", location='json')
        parser.add_argument('field_player', type=int, required=True, help="Field player cannot be missing!", location='json')
        parser.add_argument('field_player_sub', type=bool, required=True, help="Field player substitute cannot be missing!", location='json')
        parser.add_argument('field_pos', type=int, location='json')

        #team A detail
        parser.add_argument('team_a', type=int, required=True, help="Team id cannot be missing!", location='json')
        parser.add_argument('team_a_name', type=str, required=True, help="Team A name cannot be missing!", location='json')
        parser.add_argument('team_a_srt_name', type=str, required=True, help="Team A short name cannot be missing!", location='json')      
        parser.add_argument('team_a_score', type=int, required=True, help="Team score cannot be missing!", location='json')        
        parser.add_argument('team_a_over', type=float, required=True, help="Team over cannot be missing!", location='json')
        parser.add_argument('team_a_wicket', type=int, required=True, help="Team wicket cannot be missing!", location='json')
        parser.add_argument('team_a_target', type=int, required=True, help="Team target cannot be missing!", location='json')
        
        #team b detail
        parser.add_argument('team_b', type=int, required=True, help="Team id cannot be missing!", location='json')        
        parser.add_argument('team_b_name', type=str, required=True, help="Team B name cannot be missing!", location='json')
        parser.add_argument('team_b_srt_name', type=str, required=True, help="Team B short name cannot be missing!", location='json')
        parser.add_argument('team_b_score', type=int, required=True, help="Team score cannot be missing!", location='json')        
        parser.add_argument('team_b_over', type=float, required=True, help="Team over cannot be missing!", location='json')
        parser.add_argument('team_b_wicket', type=int, required=True, help="Team wicket cannot be missing!", location='json')
        parser.add_argument('team_b_target', type=int, required=True, help="Team target cannot be missing!", location='json')
        
        #innings detail
        parser.add_argument('run_scored', type=int, required=True, help="Run scored cannot be missing!", location='json')
        parser.add_argument('innings', type=int, required=True, help="Innings cannot be missing!", location='json')
        parser.add_argument('curr_rate', type=float, required=True, help="Current run rate cannot be missing!", location='json')
        parser.add_argument('req_rate', type=float, required=True, help="Required run rate cannot be missing!", location='json')
        
        #extras detail
        parser.add_argument('byes', type=int, required=True, help="Byes cannot be missing!", location='json')
        parser.add_argument('leg_byes', type=int, required=True, help="Leg byes cannot be missing!", location='json')
        parser.add_argument('wide', type=int, required=True, help="Wide cannot be missing!", location='json')
        parser.add_argument('no_ball', type=int, required=True, help="No ball cannot be missing!", location='json')
        parser.add_argument('penalty_a', type=int, required=True, help="Penalty A cannot be missing!", location='json')
        parser.add_argument('penalty_b', type=int, required=True, help="Penalty B cannot be missing!", location='json')
        parser.add_argument('powerplay', type=str, required=True, help="Power play cannot be missing!", location='json')
        parser.add_argument('recent', type=str, required=True, help="Recent balls info cannot be missing!", location='json')
        parser.add_argument('match_status', type=int, required=True, help="Match Status cannot be missing!", location='json')
        parser.add_argument('match_status_name', type=str, required=True, help="Match Status name cannot be missing!", location='json')
        parser.add_argument('rvs_a_target', type=int, required=True, help="Revised target cannot be missing!", location='json')
        parser.add_argument('rvs_a_over', type=float, required=True, help="Revised over A cannot be missing!", location='json')
        parser.add_argument('rvs_b_over', type=float, required=True, help="Revised over B cannot be missing!", location='json')
        
        #play type
        parser.add_argument('ball_type_name', type=str, required=True, help="Ball type name cannot be missing!", location='json')
        parser.add_argument('shot_type_name', type=str, required=True, help="Shot type name cannot be missing!", location='json')
        parser.add_argument('ball_type', type=int, required=True, help="Ball type cannot be missing!", location='json')
        parser.add_argument('shot_type', type=int, required=True, help="Shot type cannot be missing!", location='json')
        
        #format info
        parser.add_argument('format_name', type=str, required=True, help="Format name cannot be missing!", location='json')
        parser.add_argument('format_overs', type=int, required=True, help="Format overs cannot be missing!", location='json')
        
        #comment
        parser.add_argument('comment', type=str, required=True, help="Comment cannot be missing!", location='json')
        parser.add_argument('c_id', type=int, location='json')

        # updated details
        parser.add_argument('modified', type=str, required=True, help="Modified cannot be missing!", location='json')
        parser.add_argument('created', type=str, required=True, help="Modified cannot be missing!", location='json')

        #validation
        args = parser.parse_args()
        try:
            query_match= """
                SELECT SCORE_ID FROM MATCH WHERE ID = %s
                """
            params = (args['match_id'],)
            row_score = readSQL(query_match, params)
            if row_score:
                query_score= """
                SELECT SCORECARD_ID FROM SCORE WHERE ID = %s
                """
                params = (row_score['score_id'],)
                row_scorecard_id = readSQL(query_score, params)
                
            if row_scorecard_id:
                try:    
                    # key formation/creation - fullscore card
                    get_key = ''
                    if args['innings'] == 1:
                        overs = args['team_a_over']
                    elif args['innings'] == 2:
                        overs = args['team_b_over']
                        app.redis.set("match:"+str(args['match_id'])+":innings", args['innings'])
                    
                    get_curr_inngs = app.redis.get("match:"+str(args['match_id'])+":innings")
                    get_inngs = json.loads(get_curr_inngs)
                    
                    ball_prev = 0.0
                    counter = 0
                    get_key = "livescorecard:"+str(args['match_id'])+":current:"+str(get_inngs)
                    if(app.redis.get(get_key)):
                        prev = app.redis.get(get_key)
                        ball_prev = json.loads(prev)
                        counter = ball_prev['ball']
                        # create a existing key
                        if(str(counter)):
                            counter_ballid = counter
                            key_creation_counter = counter + 1
                            key_prv_counter = counter
                            # create a new fullscore card previous key
                            fullscorecard_key_prv = "fullscorecard:"+str(args['match_id'])+":"+str(args['innings'])+":"+str(key_prv_counter)
                            # create a new fullscore card key
                            fullscorecard_key = "fullscorecard:"+str(args['match_id'])+":"+str(args['innings'])+":"+str(key_creation_counter)
                    
                    fullscorecard_key_inning_1 = ''
                    fullscorecard_key_inning_2 = ''
                    # create a initial key for 1st innings
                    if(args['innings'] == 1 and overs == 0 and counter == 0):
                        fullscorecard_key_inning_1 = "fullscorecard:"+str(args['match_id'])
                    elif(args['innings'] == 1 and overs == 0.1 and counter == 0):
                        fullscorecard_key_inning_1 = "fullscorecard:"+str(args['match_id'])
                    elif(args['innings'] == 1):
                        fullscorecard_key_inning_1 = fullscorecard_key_prv
                    
                    # create a initial key for 2nd innings
                    if(args['innings'] == 2 and overs == 0 and counter == 0):
                        fullscorecard_key_inning_2 = "fullscorecard:"+str(args['match_id'])+":current"
                    elif(args['innings'] == 2 and overs == 0.1 and counter == 0):
                        # setting for the 0th ball of inning 2
                        fullscorecard_key_init = "fullscorecard:"+str(args['match_id'])+":"+str(args['innings'])+":"+str(0)
                        full_obj_init = app.redis.get("fullscorecard:"+str(args['match_id'])+":current")
                        app.redis.set(fullscorecard_key_init, full_obj_init)

                        fullscorecard_key_inning_2 = "fullscorecard:"+str(args['match_id'])+":current"
                    elif(args['innings'] == 2):
                        fullscorecard_key_inning_2 = fullscorecard_key_prv
                    # to get the match name
                    query_matchname= """
                    SELECT NAME FROM MATCH WHERE ID = %s
                    """
                    params = (args['match_id'], )
                    row_matchname = readSQL(query_matchname, params)
                    match_name = ''
                    if row_matchname:
                        match_name = row_matchname
                    else:
                        match_name = ''

                    # for the first ball - innings 1
                    if(app.redis.get(fullscorecard_key_inning_1) and args['innings'] == 1):
                        full_obj = app.redis.get(fullscorecard_key_inning_1)
                        obj = json.loads(full_obj)
                        str_striker = str(args['striker'])+"_pname"
                        str_non_striker = str(args['non_striker'])+"_pname"
                        str_cur_bowler = str(args['cur_bowler'])+"_pname"
                        # match name
                        obj['name'] = match_name['name']
                        #livescore card info
                        obj['currentInnings'] = args['innings']
                        obj['match_id'] = args['match_id']
                        obj['teamA'] = args['team_a_name']
                        obj['teamAOvers'] = args['team_a_over']
                        obj['teamARuns'] = args['team_a_score']
                        obj['teamAWickets'] = args['team_a_wicket']
                        obj['teamB'] = args['team_b_name']
                        obj['teamBOvers'] = args['team_b_over']
                        obj['teamBRuns'] = args['team_b_score']
                        obj['teamBWickets'] = args['team_b_wicket']
                        obj['strikerId'] = args['striker']
                        obj['strikerName'] = args['striker_name']
                        obj['DisplayStrikerName'] = args['display_striker_name']
                        obj['strikerRuns'] = args['striker_run'] 
                        obj['strikerFour'] = args['striker_4']
                        obj['strikerSix'] = args['striker_6']
                        obj['strikerStrikeRate'] = args['striker_strikerate']
                        obj['strikerBalls'] = args['striker_balls']
                        obj['nonStrikerId'] = args['non_striker']
                        obj['NonStrikerName'] = args['non_striker_name']
                        obj['DisplayNonStrikerName'] = args['display_non_striker_name']
                        obj['NonStrikerRuns'] = args['non_striker_run'] 
                        obj['NonStrikerFour'] = args['non_striker_4']
                        obj['NonStrikerSix'] = args['non_striker_6']
                        obj['NonStrikerStrikeRate'] = args['non_striker_strikerate']
                        obj['NonStrikerBalls'] = args['non_striker_balls']
                        obj['bowlerName'] = args['cur_bowler_name']
                        obj['bowlerOver'] = args['cur_bowler_over']
                        obj['bowlerEconomy'] = args['cur_bowler_eco']
                        obj['bowlerMaiden'] = args['cur_bowler_mai']
                        obj['bowlerWicket'] = args['cur_bowler_wic']
                        obj['bowlerRuns'] = args['cur_bowler_run']
                        obj['recent'] = args['recent']
                        obj['curr_rate'] = args['curr_rate']
                        obj['req_rate'] = args['req_rate']
                        obj['rvs_a_target'] = args['rvs_a_target']
                        obj['rvs_a_over'] = args['rvs_a_over']
                        obj['rvs_b_over'] = args['rvs_b_over']
                        obj['format_name'] = args['format_name']
                        obj['format_overs'] = args['format_overs']
                        obj['striker_first_name'] = args['striker_first_name']
                        obj['striker_last_name'] = args['striker_last_name']
                        obj['non_striker_first_name'] = args['non_striker_first_name']
                        obj['non_striker_last_name'] = args['non_striker_last_name']
                        obj['cur_bowler_first_name'] = args['cur_bowler_first_name']
                        obj['cur_bowler_last_name'] = args['cur_bowler_last_name']
                        obj['team_a_srt_name'] = args['team_a_srt_name']
                        obj['team_b_srt_name'] = args['team_b_srt_name']
                        obj['prv_bowler']=args['prv_bowler']
                        obj['prv_bowler_over']=args['prv_bowler_over']
                        obj['prv_bowler_eco']=args['prv_bowler_eco']
                        obj['prv_bowler_mai']=args['prv_bowler_mai']
                        obj['prv_bowler_wic']=args['prv_bowler_wic']
                        obj['prv_bowler_run']=args['prv_bowler_run']
                        obj['prv_bowler_first_name'] = args['prv_bowler_first_name']
                        obj['prv_bowler_last_name'] = args['prv_bowler_last_name']
                        obj['prv_bowler_name']=args['prv_bowler_name']
                        # obj['match_status'] = args['match_status_name']
                        # innings 1 info
                        if(args['innings'] == 1):
                            if(obj['innings_1']['batting']):
                                striker_status = 'not out'
                                non_striker_status = 'not out'
                                # out method
                                if(args['striker_out'] or args['non_striker_out']):
                                    if(args['striker_out']):
                                        if(args['striker_out_name'] == 'Caught' or args['striker_out_name'] == 'Run Out' or args['striker_out_name'] == 'Stumped' ):
                                            out_method = ''
                                            if(args['striker_out_name'] == 'Run Out'):
                                                out_method = 'run out'
                                            elif(args['striker_out_name'] == 'Caught'):
                                                out_method = 'c'
                                            elif(args['striker_out_name'] == 'Stumped'):
                                                out_method = 'st'
                                            if(args['field_player_sub']):
                                                striker_status = out_method+' (sub)'+args['field_player_name']+' b '+args['cur_bowler_name']
                                            else:
                                                striker_status = out_method+' '+args['field_player_name']+' b '+args['cur_bowler_name']
                                        elif(args['striker_out_name'] == 'Bowled' or args['striker_out_name'] == 'LBW' or args['striker_out_name'] == 'Caught & Bowled' or args['striker_out_name'] == 'Obstructing the field' or args['striker_out_name'] == 'Hit wicket' or args['striker_out_name'] == 'Hit the ball twice' ):
                                            out_method = ''
                                            if(args['striker_out_name'] == 'LBW'):
                                                out_method = 'lbw '
                                            elif(args['striker_out_name'] == 'Caught & Bowled'):
                                                out_method = 'c&'
                                            elif(args['striker_out_name'] == 'Obstructing the field'):
                                                out_method = 'obs '
                                            elif(args['striker_out_name'] == 'Hit wicket'):
                                                out_method = 'hit wicket '
                                            elif(args['striker_out_name'] == 'Hit the ball twice'):
                                                out_method = 'hit the ball twice '
                                            striker_status = out_method+'b '+args['cur_bowler_name']
                                        elif(args['striker_out_name'] == 'Timed out'):
                                            striker_status = 'timed out'
                                        # fall of wickets
                                        val = str(args['team_a_score'])+'/'+str(args['team_a_wicket'])+' ('+args['striker_name']+','+str(overs)+' ov)'
                                        obj['innings_1']['fallOfWickets'].append(val)
                                    elif(args['non_striker_out']):
                                        if(args['non_striker_out_name'] == 'Run Out'):
                                            out_method = ''
                                            if(args['non_striker_out_name'] == 'Run Out'):
                                                out_method = 'run out'
                                            if(args['field_player_sub']):
                                                non_striker_status = out_method+' (sub)'+args['field_player_name']+' b '+args['cur_bowler_name']
                                            else:
                                                non_striker_status = out_method+' '+args['field_player_name']+' b '+args['cur_bowler_name']
                                        elif(args['non_striker_out_name'] == 'Timed out'):
                                            non_striker_status = 'timed out'
                                        # fall of wickets
                                        val = str(args['team_a_score'])+'/'+str(args['team_a_wicket'])+' ('+args['non_striker_name']+','+str(overs)+' ov)'
                                        obj['innings_1']['fallOfWickets'].append(val)
                                # Yet to bat
                                if obj['innings_1']['yetToBat']:
                                    if args['striker_name'] in obj['innings_1']['yetToBat']:
                                        obj['innings_1']['yetToBat'].remove(args['striker_name'])        
                                obj['innings_1']['batting'][str_striker] = { 'id' : args['striker'], 'name' : args['striker_name'], 'status': striker_status, 'run': args['striker_run'], 
                                                                        'first_name' : args['striker_first_name'],
                                                                        'last_name' : args['striker_last_name'],
                                                                        'four' : args['striker_4'],
                                                                        'six' : args['striker_6'],
                                                                        'strikeRate' : args['striker_strikerate'],
                                                                        'batting_style' : args['striker_batting_style'],
                                                                        'balls' : args['striker_balls'], 'position': args['striker_position'] }
                                # Yet to bat
                                if obj['innings_1']['yetToBat']:
                                    if args['non_striker_name'] in obj['innings_1']['yetToBat']:
                                        obj['innings_1']['yetToBat'].remove(args['non_striker_name'])
                                obj['innings_1']['batting'][str_non_striker] = { 'id' : args['non_striker'], 'name' : args['non_striker_name'], 'status': non_striker_status, 'run': args['non_striker_run'], 
                                                                            'first_name' : args['non_striker_first_name'],
                                                                            'last_name' : args['non_striker_last_name'],
                                                                            'four' : args['non_striker_4'],
                                                                            'six' : args['non_striker_6'],
                                                                            'strikeRate' : args['non_striker_strikerate'],
                                                                            'batting_style' : args['non_striker_batting_style'],
                                                                            'balls' : args['non_striker_balls'], 'position': args['non_striker_position'] }
                            obj['innings_1']['totalRuns'] = args['team_a_score']
                            obj['innings_1']['totalWickets'] = args['team_a_wicket']
                            obj['innings_1']['totalOvers'] = args['team_a_over']
                            if(obj['innings_1']['extras']):
                                obj['innings_1']['extras']['byes'] =  args['byes']
                                obj['innings_1']['extras']['legByes'] = args['leg_byes']
                                obj['innings_1']['extras']['wide'] = args['wide']
                                obj['innings_1']['extras']['noBall'] = args['no_ball']
                                obj['innings_1']['extras']['pnlt'] = args['penalty_a']
                            if str_cur_bowler in obj['innings_1']['Bowling']:
                                obj['innings_1']['Bowling'][str_cur_bowler] = { 'id' : args['cur_bowler'], 'name' : args['cur_bowler_name'], 'over':  args['cur_bowler_over'],
                                                                            'first_name' : args['cur_bowler_first_name'],
                                                                            'last_name' : args['cur_bowler_last_name'],
                                                                            'economy': args['cur_bowler_eco'],
                                                                            'maiden': args['cur_bowler_mai'],
                                                                            'wicket': args['cur_bowler_wic'],
                                                                            'bowling_cat': args['cur_bowler_bowling_cat'],
                                                                            'run': args['cur_bowler_run']}
                            else:
                                obj['innings_1']['Bowling'][str_cur_bowler] = {}
                                obj['innings_1']['Bowling'][str_cur_bowler] = { 'id' : args['cur_bowler'], 'name' : args['cur_bowler_name'], 'over':  args['cur_bowler_over'],
                                                                            'first_name' : args['cur_bowler_first_name'],
                                                                            'last_name' : args['cur_bowler_last_name'],
                                                                            'economy': args['cur_bowler_eco'],
                                                                            'maiden': args['cur_bowler_mai'],
                                                                            'wicket': args['cur_bowler_wic'],
                                                                            'bowling_cat': args['cur_bowler_bowling_cat'],
                                                                            'run': args['cur_bowler_run']}
                        app.redis.set(fullscorecard_key, json.dumps(obj))
                        app.redis.set(get_key, json.dumps({'over': str(overs), 'innings': args['innings'], 'ball': counter + 1, 'match_status': args['match_status_name']}))
                        app.redis.set("fullscorecard:"+str(args['match_id'])+":current", json.dumps(obj))
                    #inning 2, calculation for the first ball of the innings
                    elif(app.redis.get(fullscorecard_key_inning_2) and args['innings'] == 2):
                        str_striker = str(args['striker'])+"_pname"
                        str_non_striker = str(args['non_striker'])+"_pname"
                        str_cur_bowler = str(args['cur_bowler'])+"_pname"
                        # create a new fullscore card key
                        full_obj = app.redis.get(fullscorecard_key_inning_2)
                        obj = json.loads(full_obj)
                        # match name
                        obj['name'] = match_name['name']
                        #livescore card info
                        obj['currentInnings'] = args['innings']
                        obj['match_id'] = args['match_id']
                        obj['teamA'] = args['team_a_name']
                        obj['teamAOvers'] = args['team_a_over']
                        obj['teamARuns'] = args['team_a_score']
                        obj['teamAWickets'] = args['team_a_wicket']
                        obj['teamB'] = args['team_b_name']
                        obj['teamBOvers'] = args['team_b_over']
                        obj['teamBRuns'] = args['team_b_score']
                        obj['teamBWickets'] = args['team_b_wicket']
                        obj['strikerId'] = args['striker']
                        obj['strikerName'] = args['striker_name']
                        obj['DisplayStrikerName'] = args['display_striker_name']
                        obj['strikerRuns'] = args['striker_run'] 
                        obj['strikerFour'] = args['striker_4']
                        obj['strikerSix'] = args['striker_6']
                        obj['strikerStrikeRate'] = args['striker_strikerate']
                        obj['strikerBalls'] = args['striker_balls']
                        obj['nonStrikerId'] = args['non_striker']
                        obj['NonStrikerName'] = args['non_striker_name']
                        obj['DisplayNonStrikerName'] = args['display_non_striker_name']
                        obj['NonStrikerRuns'] = args['non_striker_run'] 
                        obj['NonStrikerFour'] = args['non_striker_4']
                        obj['NonStrikerSix'] = args['non_striker_6']
                        obj['NonStrikerStrikeRate'] = args['non_striker_strikerate']
                        obj['NonStrikerBalls'] = args['non_striker_balls']
                        obj['bowlerName'] = args['cur_bowler_name']
                        obj['bowlerOver'] = args['cur_bowler_over']
                        obj['bowlerEconomy'] = args['cur_bowler_eco']
                        obj['bowlerMaiden'] = args['cur_bowler_mai']
                        obj['bowlerWicket'] = args['cur_bowler_wic']
                        obj['bowlerRuns'] = args['cur_bowler_run']
                        obj['recent'] = args['recent']
                        obj['curr_rate'] = args['curr_rate']
                        obj['req_rate'] = args['req_rate']
                        obj['rvs_a_target'] = args['rvs_a_target']
                        obj['rvs_a_over'] = args['rvs_a_over']
                        obj['rvs_b_over'] = args['rvs_b_over']
                        obj['format_name'] = args['format_name']
                        obj['format_overs'] = args['format_overs']
                        obj['striker_first_name'] = args['striker_first_name']
                        obj['striker_last_name'] = args['striker_last_name']
                        obj['non_striker_first_name'] = args['non_striker_first_name']
                        obj['non_striker_last_name'] = args['non_striker_last_name']
                        obj['cur_bowler_first_name'] = args['cur_bowler_first_name']
                        obj['cur_bowler_last_name'] = args['cur_bowler_last_name']
                        obj['team_a_srt_name'] = args['team_a_srt_name']
                        obj['team_b_srt_name'] = args['team_b_srt_name']
                        obj['prv_bowler']=args['prv_bowler']
                        obj['prv_bowler_over']=args['prv_bowler_over']
                        obj['prv_bowler_eco']=args['prv_bowler_eco']
                        obj['prv_bowler_mai']=args['prv_bowler_mai']
                        obj['prv_bowler_wic']=args['prv_bowler_wic']
                        obj['prv_bowler_run']=args['prv_bowler_run']
                        obj['prv_bowler_first_name'] = args['prv_bowler_first_name']
                        obj['prv_bowler_last_name'] = args['prv_bowler_last_name']
                        obj['prv_bowler_name']=args['prv_bowler_name']
                        # obj['match_status'] = args['match_status_name']
                        if(obj['innings_2']['batting']):
                            striker_status = 'not out'
                            non_striker_status = 'not out'
                            # out method
                            if(args['striker_out'] or args['non_striker_out']):
                                if(args['striker_out']):
                                    if(args['striker_out_name'] == 'Caught' or args['striker_out_name'] == 'Run Out' or args['striker_out_name'] == 'Stumped'):
                                        out_method = ''
                                        if(args['striker_out_name'] == 'Run Out'):
                                            out_method = 'run out'
                                        elif(args['striker_out_name'] == 'Caught'):
                                            out_method = 'c'
                                        elif(args['striker_out_name'] == 'Stumped'):
                                            out_method = 'st'
                                        if(args['field_player_sub']):
                                            striker_status = out_method+' (sub)'+args['field_player_name']+' b '+args['cur_bowler_name']
                                        else:
                                            striker_status = out_method+' '+args['field_player_name']+' b '+args['cur_bowler_name']
                                    elif(args['striker_out_name'] == 'Bowled' or args['striker_out_name'] == 'LBW' or args['striker_out_name'] == 'Caught & Bowled' or args['striker_out_name'] == 'Obstructing the field' or args['striker_out_name'] == 'Hit wicket' or args['striker_out_name'] == 'Hit the ball twice' ):
                                        out_method = ''
                                        if(args['striker_out_name'] == 'LBW'):
                                            out_method = 'lbw '
                                        elif(args['striker_out_name'] == 'Caught & Bowled'):
                                            out_method = 'c&'
                                        elif(args['striker_out_name'] == 'Obstructing the field'):
                                            out_method = 'obs '
                                        elif(args['striker_out_name'] == 'Hit wicket'):
                                            out_method = 'hit wicket '
                                        elif(args['striker_out_name'] == 'Hit the ball twice'):
                                            out_method = 'hit the ball twice '
                                        striker_status = out_method+'b '+args['cur_bowler_name']
                                    elif(args['striker_out_name'] == 'Timed out'):
                                        striker_status = 'timed out'
                                    # fall of wickets
                                    val = str(args['team_b_score'])+'/'+str(args['team_b_wicket'])+' ('+args['striker_name']+','+str(overs)+' ov)'
                                    obj['innings_2']['fallOfWickets'].append(val)
                                elif(args['non_striker_out']):
                                    if(args['non_striker_out_name'] == 'Run Out'):
                                        out_method = ''
                                        if(args['non_striker_out_name'] == 'Run Out'):
                                            out_method = 'run out'
                                        if(args['field_player_sub']):
                                            non_striker_status = out_method+' (sub)'+args['field_player_name']+' b '+args['cur_bowler_name']
                                        else:
                                            non_striker_status = out_method+' '+args['field_player_name']+' b '+args['cur_bowler_name']
                                    elif(args['non_striker_out_name'] == 'Timed out'):
                                        non_striker_status = 'timed out'
                                    # fall of wickets
                                    val = str(args['team_b_score'])+'/'+str(args['team_b_wicket'])+' ('+args['non_striker_name']+','+str(overs)+' ov)'
                                    obj['innings_2']['fallOfWickets'].append(val)
                            # Yet to bat
                            if obj['innings_2']['yetToBat']:
                                if args['striker_name'] in obj['innings_2']['yetToBat']:
                                    obj['innings_2']['yetToBat'].remove(args['striker_name'])
                            obj['innings_2']['batting'][str_striker] = { 'id' : args['striker'], 'name' : args['striker_name'], 'status': striker_status, 'run': args['striker_run'], 
                                                                    'first_name' : args['striker_first_name'],
                                                                    'last_name' : args['striker_last_name'],
                                                                    'four' : args['striker_4'],
                                                                    'six' : args['striker_6'],
                                                                    'strikeRate' : args['striker_strikerate'],
                                                                    'batting_style' : args['striker_batting_style'],
                                                                    'balls' : args['striker_balls'], 'position': args['striker_position'] }
                            # Yet to bat
                            if obj['innings_2']['yetToBat']:
                                if args['non_striker_name'] in obj['innings_2']['yetToBat']:
                                    obj['innings_2']['yetToBat'].remove(args['non_striker_name'])
                            obj['innings_2']['batting'][str_non_striker] = { 'id' : args['non_striker'], 'name' : args['non_striker_name'], 'status': non_striker_status, 'run': args['non_striker_run'], 
                                                                        'first_name' : args['non_striker_first_name'],
                                                                        'last_name' : args['non_striker_last_name'],
                                                                        'four' : args['non_striker_4'],
                                                                        'six' : args['non_striker_6'],
                                                                        'strikeRate' : args['non_striker_strikerate'],
                                                                        'batting_style' : args['non_striker_batting_style'],
                                                                        'balls' : args['non_striker_balls'], 'position': args['non_striker_position'] }
                        obj['innings_2']['totalRuns'] = args['team_b_score']
                        obj['innings_2']['totalWickets'] = args['team_b_wicket']
                        obj['innings_2']['totalOvers'] = args['team_b_over']
                        if(obj['innings_2']['extras']):
                            obj['innings_2']['extras']['byes'] =  args['byes']
                            obj['innings_2']['extras']['legByes'] = args['leg_byes']
                            obj['innings_2']['extras']['wide'] = args['wide']
                            obj['innings_2']['extras']['noBall'] = args['no_ball']
                            obj['innings_2']['extras']['pnlt'] = args['penalty_b']
                        if str_cur_bowler in obj['innings_2']['Bowling']:
                            obj['innings_2']['Bowling'][str_cur_bowler] = { 'id' : args['cur_bowler'], 'name' : args['cur_bowler_name'], 'over':  args['cur_bowler_over'],
                                                                        'first_name' : args['cur_bowler_first_name'],
                                                                        'last_name' : args['cur_bowler_last_name'],
                                                                        'economy': args['cur_bowler_eco'],
                                                                        'maiden': args['cur_bowler_mai'],
                                                                        'wicket': args['cur_bowler_wic'],
                                                                        'bowling_cat': args['cur_bowler_bowling_cat'],
                                                                        'run': args['cur_bowler_run']}
                        else:
                            obj['innings_2']['Bowling'][str_cur_bowler] = {}
                            obj['innings_2']['Bowling'][str_cur_bowler] = { 'id' : args['cur_bowler'], 'name' : args['cur_bowler_name'], 'over':  args['cur_bowler_over'],
                                                                        'first_name' : args['cur_bowler_first_name'],
                                                                        'last_name' : args['cur_bowler_last_name'],
                                                                        'economy': args['cur_bowler_eco'],
                                                                        'maiden': args['cur_bowler_mai'],
                                                                        'wicket': args['cur_bowler_wic'],
                                                                        'bowling_cat': args['cur_bowler_bowling_cat'],
                                                                        'run': args['cur_bowler_run']}
                        app.redis.set(fullscorecard_key, json.dumps(obj))
                        app.redis.set(get_key, json.dumps({'over': str(overs), 'innings': args['innings'], 'ball': counter + 1, 'match_status': args['match_status_name']}))
                except Exception as e:
                    print(e)
                    app.log.exception(e)

                # commentry redis key
                try:
                    if args['innings'] == 1:
                        overs = args['team_a_over']
                    elif args['innings'] == 2:
                        overs = args['team_b_over']
                    commentry_key_list = "list:"+str(args['match_id'])+":"+str(args['innings'])
                    commentry_key = "commentry:"+str(args['match_id'])+":"+str(args['innings'])+":"+str(key_creation_counter)
                    hash_key = "commentry:"+str(args['match_id'])+":"+str(args['innings'])
                    comm_obj = {}
                    comm_obj['comment'] = args['comment']
                    comm_obj['ball_id'] = key_creation_counter
                    comm_obj['recent'] = args['recent']
                    comm_obj['over'] = overs
                    comm_obj['innings'] = args['innings']
                    comm_obj['teamA'] = args['team_a_name']
                    comm_obj['teamB'] = args['team_b_name']
                    comm_obj['teamARuns'] = args['team_a_score']
                    comm_obj['teamBRuns'] = args['team_b_score']
                    comm_obj['teamAWickets'] = args['team_a_wicket']
                    comm_obj['teamBWickets'] = args['team_b_wicket']
                    comm_obj['strikerName'] = args['striker_name']
                    comm_obj['strikerRuns'] = args['striker_run']
                    comm_obj['strikerBalls'] = args['striker_balls']
                    comm_obj['NonStrikerName'] = args['non_striker_name']
                    comm_obj['NonStrikerRuns'] = args['non_striker_run']
                    comm_obj['NonStrikerBalls'] = args['non_striker_balls']
                    comm_obj['bowlerName'] = args['cur_bowler_name']
                    comm_obj['bowlerOver'] = args['cur_bowler_over']
                    comm_obj['bowlerMaiden'] = args['cur_bowler_mai']
                    comm_obj['bowlerWicket'] = args['cur_bowler_wic']
                    comm_obj['bowlerRuns'] = args['cur_bowler_run']
                    comm_obj['fallOfWickets'] = ''
                    comm_obj['method'] = ''
                    # out method
                    if(args['striker_out'] or args['non_striker_out']):
                        if(args['striker_out']):
                            if(args['striker_out_name'] == 'Caught' or args['striker_out_name'] == 'Run Out' or args['striker_out_name'] == 'Stumped'):
                                out_method = ''
                                if(args['striker_out_name'] == 'Run Out'):
                                    out_method = 'run out'
                                elif(args['striker_out_name'] == 'Caught'):
                                    out_method = 'c'
                                elif(args['striker_out_name'] == 'Stumped'):
                                    out_method = 'st'
                                if(args['field_player_sub']):
                                    status = out_method+' (sub)'+args['field_player_name']+' b '+args['cur_bowler_name']
                                else:
                                    status = out_method+' '+args['field_player_name']+' b '+args['cur_bowler_name']
                            elif(args['striker_out_name'] == 'Bowled' or args['striker_out_name'] == 'LBW' or args['striker_out_name'] == 'Caught & Bowled' or args['striker_out_name'] == 'Obstructing the field' or args['striker_out_name'] == 'Hit wicket' or args['striker_out_name'] == 'Hit the ball twice' ):
                                out_method = ''
                                if(args['striker_out_name'] == 'LBW'):
                                    out_method = 'lbw '
                                elif(args['striker_out_name'] == 'Caught & Bowled'):
                                    out_method = 'c&'
                                elif(args['striker_out_name'] == 'Obstructing the field'):
                                    out_method = 'obs '
                                elif(args['striker_out_name'] == 'Hit wicket'):
                                    out_method = 'hit wicket '
                                elif(args['striker_out_name'] == 'Hit the ball twice'):
                                    out_method = 'hit the ball twice '
                                status = out_method+'b '+args['cur_bowler_name']
                            elif(args['striker_out_name'] == 'Timed out'):
                                striker_status = 'timed out'
                            # fall of wickets
                            if args['innings'] == 1:
                                val = str(args['team_a_score'])+'/'+str(args['team_a_wicket'])+' ('+args['striker_name']+','+str(overs)+' ov)'
                            elif args['innings'] == 2:
                                val = str(args['team_b_score'])+'/'+str(args['team_b_wicket'])+' ('+args['striker_name']+','+str(overs)+' ov)'
                            comm_obj['fallOfWickets'] = val
                        elif(args['non_striker_out']):
                            if(args['non_striker_out_name'] == 'Run Out'):
                                out_method = ''
                                if(args['non_striker_out_name'] == 'Run Out'):
                                    out_method = 'run out'
                                    if(args['field_player_sub']):
                                        status = out_method+' (sub)'+args['field_player_name']+' b '+args['cur_bowler_name']
                                    else:
                                        status = out_method+' '+args['field_player_name']+' b '+args['cur_bowler_name']
                                elif(args['non_striker_out_name'] == 'Timed out'):
                                    status = 'timed out'
                            # fall of wickets
                            if args['innings'] == 1:
                                val = str(args['team_a_score'])+'/'+str(args['team_a_wicket'])+' ('+args['non_striker_name']+','+str(overs)+' ov)'
                            elif args['innings'] == 2:
                                val = str(args['team_b_score'])+'/'+str(args['team_b_wicket'])+' ('+args['non_striker_name']+','+str(overs)+' ov)'
                            comm_obj['fallOfWickets'] = val
                        comm_obj['method'] = status
                    app.redis.lpush(commentry_key_list,commentry_key)
                    app.redis.hset(hash_key, str(key_creation_counter), json.dumps(comm_obj))
                except Exception as e:
                    print(e)
                    app.log.exception(e)
                
                # radar/pitch chart keys
                try:
                    right_region = {
                        'Leg Glance': "8",
                        'Hook': "7",
                        'Pull': "6",
                        'On drive': "5",
                        'Off drive': "4",
                        'Cover Drive': "3",
                        'Square cut': "2",
                        'Late cut': "1"
                    }
                    left_region = {
                        'Leg Glance': "1",
                        'Hook': "2",
                        'Pull': "3",
                        'On drive': "4",
                        'Off drive': "5",
                        'Cover Drive': "6",
                        'Square cut': "7",
                        'Late cut': "8"
                    }
                    
                    radar_key = 'radar:'+str(args['match_id'])+":"+str(args['innings'])
                    if app.redis.hget(radar_key, args['striker']):
                        val = app.redis.hget(radar_key, args['striker'])
                        if args['striker_batting_style'] == 'Right-handed':
                            loaded_val = json.loads(val)
                            if args['shot_type_name'] in right_region:
                                if right_region[args['shot_type_name']] in loaded_val:
                                    for key, value in loaded_val.items() :
                                        if key == right_region[args['shot_type_name']]:
                                            loaded_val[key] = value + args['run_scored']
                                else:
                                    loaded_val[right_region[args['shot_type_name']]] = args['run_scored']
                                app.redis.hset(radar_key, args['striker'], json.dumps(loaded_val))
                        if args['striker_batting_style'] == 'Left-handed':
                            loaded_val = json.loads(val)
                            if args['shot_type_name'] in left_region:
                                if left_region[args['shot_type_name']] in loaded_val:
                                    for key, value in loaded_val.items() :
                                        if key == left_region[args['shot_type_name']]:
                                            loaded_val[key] = value + args['run_scored']
                                else:
                                    loaded_val[left_region[args['shot_type_name']]] = args['run_scored']
                                app.redis.hset(radar_key, args['striker'], json.dumps(loaded_val))
                    else:
                        obj = {}
                        if args['striker_batting_style'] == 'Right-handed':
                            if args['shot_type_name'] in right_region:
                                obj[left_region[args['shot_type_name']]] = args['run_scored']
                                app.redis.hset(radar_key, args['striker'], json.dumps(obj))
                        if args['striker_batting_style'] == 'Left-handed':
                            if args['shot_type_name'] in left_region:
                                obj[left_region[args['shot_type_name']]] = args['run_scored']
                                app.redis.hset(radar_key, args['striker'], json.dumps(obj))
                except Exception as e:
                    print(e)
                    app.log.exception(e)

                #pitch chart
                try:
                    if args['ball_type_name'] == 'Short' or args['ball_type_name'] == 'Good length' or args['ball_type_name'] == 'Fuller length':
                        pitch_key = 'pitch:'+str(args['match_id'])+":"+str(args['innings'])
                        if app.redis.hget(pitch_key, args['cur_bowler']):
                            val = app.redis.hget(pitch_key, args['cur_bowler'])
                            loaded_val = json.loads(val)
                            if args['ball_type_name'] in loaded_val:
                                for key, value in loaded_val.items() :
                                    if key == args['ball_type_name']:
                                        loaded_val[key] = loaded_val[args['ball_type_name']] + 1
                                    total_balls = int(args['cur_bowler_over']) * 6 + int(args['cur_bowler_over'] % 1 * 10)        
                                    loaded_val['total'] = total_balls
                            else:
                                total_balls = int(args['cur_bowler_over']) * 6 + int(args['cur_bowler_over'] % 1 * 10)        
                                loaded_val['total'] = total_balls
                                loaded_val[args['ball_type_name']] = 1
                            app.redis.hset(pitch_key, args['cur_bowler'], json.dumps(loaded_val))    
                        else:
                            obj = {}
                            total_balls = int(args['cur_bowler_over']) * 6 + int(args['cur_bowler_over'] % 1 * 10)
                            obj['total'] = total_balls
                            obj[args['ball_type_name']] = 1
                            app.redis.hset(pitch_key, args['cur_bowler'], json.dumps(obj))
                except Exception as e:
                    print(e)
                    app.log.exception(e)


                insert_livescore = """
                    INSERT INTO PLAYERSCORECARD (
                        s_id,
                        match_id,
                        striker,
                        striker_position,
                        striker_run, 
                        striker_4,
                        striker_6,
                        striker_strikerate,
                        striker_balls,
                        striker_out,
                        striker_wicket,
                        non_striker, 
                        non_striker_position,
                        non_striker_run,
                        non_striker_4,
                        non_striker_6,
                        non_striker_strikerate,
                        non_striker_balls,
                        non_striker_out,
                        non_striker_wicket,
                        cur_bowler, 
                        cur_bowler_over,
                        cur_bowler_eco,
                        cur_bowler_mai,
                        cur_bowler_wic,
                        cur_bowler_spell,
                        cur_bowler_run,
                        prv_bowler,
                        prv_bowler_over,
                        prv_bowler_eco,
                        prv_bowler_mai,
                        prv_bowler_wic,
                        prv_bowler_spell,
                        prv_bowler_run,
                        field_player,
                        team_a,
                        team_a_score,
                        team_a_over,
                        team_a_wicket,
                        team_a_target,
                        team_b,
                        team_b_score,
                        team_b_over,
                        team_b_wicket,
                        team_b_target,
                        run_scored,
                        innings,
                        byes,
                        leg_byes,
                        wide,
                        no_ball,
                        penalty_a,
                        penalty_b,
                        ball_type,
                        shot_type,
                        comment,
                        c_id,
                        modified,
                        created,
                        powerplay,
                        recent,
                        ball_id,
                        match_status,
                        req_rate,
                        curr_rate,
                        field_pos,
                        rvs_a_target,
                        rvs_a_over,
                        rvs_b_over
                    ) VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                """
                params_main = (
                    row_scorecard_id['scorecard_id'],
                    args['match_id'],
                    args['striker'],
                    args['striker_position'],
                    args['striker_run'], 
                    args['striker_4'],
                    args['striker_6'],
                    args['striker_strikerate'],
                    args['striker_balls'],
                    args['striker_out'],
                    args['striker_wicket'],
                    args['non_striker'], 
                    args['non_striker_position'],
                    args['non_striker_run'],
                    args['non_striker_4'],
                    args['non_striker_6'],
                    args['non_striker_strikerate'],
                    args['non_striker_balls'],
                    args['non_striker_out'],
                    args['non_striker_wicket'],
                    args['cur_bowler'], 
                    args['cur_bowler_over'],
                    args['cur_bowler_eco'],
                    args['cur_bowler_mai'],
                    args['cur_bowler_wic'],
                    args['cur_bowler_spell'],
                    args['cur_bowler_run'],
                    args['prv_bowler'],
                    args['prv_bowler_over'],
                    args['prv_bowler_eco'],
                    args['prv_bowler_mai'],
                    args['prv_bowler_wic'],
                    args['prv_bowler_spell'],
                    args['prv_bowler_run'],
                    args['field_player'],
                    args['team_a'],
                    args['team_a_score'],
                    args['team_a_over'],
                    args['team_a_wicket'],
                    args['team_a_target'],
                    args['team_b'],
                    args['team_b_score'],
                    args['team_b_over'],
                    args['team_b_wicket'],
                    args['team_b_target'],
                    args['run_scored'],
                    args['innings'],
                    args['byes'],
                    args['leg_byes'],
                    args['wide'],
                    args['no_ball'],
                    args['penalty_a'],
                    args['penalty_b'],
                    args['ball_type'],
                    args['shot_type'],
                    args['comment'],
                    args['c_id'],
                    args['modified'],
                    args['created'],
                    args['powerplay'],
                    args['recent'],
                    counter_ballid + 1,
                    args['match_status'],
                    args['req_rate'],
                    args['curr_rate'],
                    args['field_pos'],
                    args['rvs_a_target'],
                    args['rvs_a_over'],
                    args['rvs_b_over']
                )
                count = writeSQL(insert_livescore, params_main)
                if count:
                    query_playerscorecard= """
                    SELECT * FROM PLAYERSCORECARD WHERE S_ID = %s ORDER BY ID desc limit 1
                    """
                    params = (row_scorecard_id['scorecard_id'],)
                    row_playerscorecard = readSQL(query_playerscorecard, params)
                    row_card = {}
                    row_card = row_playerscorecard
                    row_card['ballid'] = counter_ballid + 1
                    row_card['striker_first_name'] = args['striker_first_name']
                    row_card['striker_last_name'] = args['striker_last_name']
                    row_card['non_striker_first_name'] = args['non_striker_first_name']
                    row_card['non_striker_last_name'] = args['non_striker_last_name']
                    row_card['cur_bowler_first_name'] = args['cur_bowler_first_name']
                    row_card['cur_bowler_last_name'] = args['cur_bowler_last_name']
                    row_card['prv_bowler_first_name'] = args['prv_bowler_first_name']
                    row_card['prv_bowler_last_name'] = args['prv_bowler_last_name']
                    row_card['prv_bowler_name']=args['prv_bowler_name']
                    row_card['team_a_srt_name'] = args['team_a_srt_name']
                    row_card['team_b_srt_name'] = args['team_b_srt_name']
                    row_card['cur_bowler_bowling_cat'] = args['cur_bowler_bowling_cat']
                    data = json.dumps({'success' : True, 'card': row_card}, default=default)
                    return json.loads(data), 200
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500
