from flask_restful import Resource, reqparse, request
from common.db import writeSQL, readSQL, readManySQL
import app, json, math
from common.util import default
from datetime import datetime

class Penalty(Resource):
    def put(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('innings', type=int, required=True, help="innings cannot be missing!", location='json')
        parser.add_argument('match_id', type=int, required=True, help="match id of the match cannot be missing!", location='json')
        parser.add_argument('ballid', type=int, required=True, help="ball id cannot be missing!", location='json')
        parser.add_argument('penalty', type=str, required=True, help="penalty cannot be missing!", location='json')
        parser.add_argument('formatOver', type=str, required=True, help="Format over cannot be missing!", location='json')
        parser.add_argument('message', type=str, required=True, help="Message cannot be missing!", location='json')
        args = parser.parse_args()
        try:
            innings = int(args['innings'])
            matchid = args['match_id']
            ballid = args['ballid']
            penalty = args['penalty']
            formatOver = int(args['formatOver']) - 1 + 0.6
            query_playerscorecard= """
                SELECT * FROM PLAYERSCORECARD WHERE MATCH_ID = %s AND INNINGS = %s ORDER BY ID desc limit 1
                """
            params = (matchid, innings)
            row_last_record = readSQL(query_playerscorecard, params)
            if(row_last_record):
                if(innings == 1):
                    # teamA is doing  mistake
                    if(penalty == 'teamA'):
                        if(row_last_record['penalty_a']):
                            pnlt_a = row_last_record['penalty_a'] + 5
                        else:
                            pnlt_a = 5
                        update_record= """
                                UPDATE PLAYERSCORECARD SET PENALTY_A = %s WHERE MATCH_ID = %s AND BALL_ID = %s
                        """
                        params = (pnlt_a, matchid, ballid)
                        updated_record = writeSQL(update_record, params)
                        if(updated_record):
                            query_playerscorecard= """
                            SELECT * FROM PLAYERSCORECARD WHERE MATCH_ID = %s AND INNINGS = %s ORDER BY ID desc limit 1
                            """
                            params = (matchid, innings)
                            row_lastrecord = readSQL(query_playerscorecard, params)
                            if(row_lastrecord):
                                pnlt = 0
                                if(row_last_record['ball_id'] == args['ballid']):
                                    pnlt = row_lastrecord['penalty_a']
                                else:
                                    if(row_last_record['penalty_a']):
                                        pnlt = row_last_record['penalty_a'] + 5
                                    else:
                                        pnlt = 5
                                get_curr_inng = app.redis.get("match:"+str(matchid)+":innings")
                                get_inng = json.loads(get_curr_inng)
                                curr_key = "livescorecard:"+str(matchid)+":current:"+str(get_inng)
                                curr_livecard = app.redis.get(curr_key)
                                key_info = json.loads(curr_livecard)
                                get_fullcard = "fullscorecard:"+str(matchid)+":"+str(innings)+":"+str(key_info['ball'])
                                fullcard = json.loads(app.redis.get(get_fullcard))
                                fullcard['teamBRuns'] = row_lastrecord['team_b_score'] + 5
                                # print(fullcard['teamBRuns'])
                                for key, value in fullcard['innings_1'].items() :
                                    if key == 'extras':
                                        fullcard['innings_1']['extras']['pnlt'] = pnlt
                                updated_key = app.redis.set(get_fullcard, json.dumps(fullcard, default=default))
                                if(updated_key):
                                    update_playerscorecard= """
                                        UPDATE PLAYERSCORECARD SET PENALTY_A = %s, TEAM_B_SCORE = %s WHERE ID = %s
                                    """
                                    params = (pnlt, row_lastrecord['team_b_score'] + 5, row_lastrecord['id'])
                                    updated_row = writeSQL(update_playerscorecard, params)
                                    if(updated_row):
                                        #manual commentry
                                        list_com = "list:"+str(matchid)+":"+str(get_inng)
                                        man_com_key = "commentry:"+str(matchid)+":"+str(get_inng)+":manual"
                                        obj = {}
                                        obj['comment'] = args['message']
                                        obj['datetime'] = datetime.utcnow()
                                        if(app.redis.hkeys(man_com_key)):
                                            index_val = [val for loc, val in enumerate(app.redis.hkeys(man_com_key)) if math.floor(float(val)) == key_info['ball']]
                                            if(index_val):
                                                max_val = float(max(index_val))
                                                field_key = format(max_val + 0.1, ".1f")
                                            else:
                                                field_key = key_info['ball'] + 0.1
                                        else:
                                            field_key = key_info['ball'] + 0.1
                                        list_man_com_key = man_com_key+":"+str(field_key)
                                        app.redis.lpush(list_com, list_man_com_key)
                                        app.redis.hset(man_com_key, field_key, json.dumps(obj, default=default))
                                        return { 'success': True }, 200
                    # teamB is doing  mistake
                    elif(penalty == 'teamB'):
                        if(row_last_record['penalty_b']):
                            pnlt_b = row_last_record['penalty_b'] + 5
                        else:
                            pnlt_b = 5
                        update_record= """
                                UPDATE PLAYERSCORECARD SET PENALTY_B = %s WHERE MATCH_ID = %s AND BALL_ID = %s
                        """
                        params = (pnlt_b, matchid, ballid)
                        updated_record = writeSQL(update_record, params)
                        if(updated_record):
                            query_playerscorecard= """
                            SELECT * FROM PLAYERSCORECARD WHERE MATCH_ID = %s AND INNINGS = %s ORDER BY ID desc limit 1
                            """
                            params = (matchid, innings)
                            row_lastrecord = readSQL(query_playerscorecard, params)
                            if(row_lastrecord):
                                pnlt = 0
                                if(row_last_record['ball_id'] == args['ballid']):
                                    pnlt = row_lastrecord['penalty_b']
                                else:
                                    if(row_last_record['penalty_b']):
                                        pnlt = row_last_record['penalty_b'] + 5
                                    else:
                                        pnlt = 5
                                score = row_lastrecord['team_a_score'] + 5
                                over = row_lastrecord['team_a_over']
                                balls = int(over) + (round(over % 1, 2) * 10 / 6)
                                cal_cur_rate = score / balls
                                get_curr_inng = app.redis.get("match:"+str(matchid)+":innings")
                                get_inng = json.loads(get_curr_inng)
                                curr_key = "livescorecard:"+str(matchid)+":current:"+str(get_inng)
                                curr_livecard = app.redis.get(curr_key)
                                key_info = json.loads(curr_livecard)
                                get_fullcard = "fullscorecard:"+str(matchid)+":"+str(innings)+":"+str(key_info['ball'])
                                fullcard = json.loads(app.redis.get(get_fullcard))
                                fullcard['teamARuns'] = score
                                fullcard['curr_rate'] = round(cal_cur_rate, 2)
                                
                                for key, value in fullcard['innings_2'].items() :
                                    if key == 'extras':
                                        fullcard['innings_2']['extras']['pnlt'] = pnlt
                                updated_key = app.redis.set(get_fullcard, json.dumps(fullcard, default=default))
                                if updated_key:
                                    update_playerscorecard= """
                                        UPDATE PLAYERSCORECARD SET TEAM_A_SCORE = %s, CURR_RATE = %s, PENALTY_B = %s WHERE ID = %s
                                    """
                                    params = (score, float(round(cal_cur_rate, 2)), pnlt, row_lastrecord['id'])
                                    updated_row = writeSQL(update_playerscorecard, params)
                                    if(updated_row):
                                        #manual commentry
                                        list_com = "list:"+str(matchid)+":"+str(get_inng)
                                        man_com_key = "commentry:"+str(matchid)+":"+str(get_inng)+":manual"
                                        obj = {}
                                        obj['comment'] = args['message']
                                        obj['datetime'] = datetime.utcnow()
                                        if(app.redis.hkeys(man_com_key)):
                                            index_val = [val for loc, val in enumerate(app.redis.hkeys(man_com_key)) if math.floor(float(val)) == key_info['ball']]
                                            if(index_val):
                                                max_val = float(max(index_val))
                                                field_key = format(max_val + 0.1, ".1f")
                                            else:
                                                field_key = key_info['ball'] + 0.1
                                        else:
                                            field_key = key_info['ball'] + 0.1
                                        list_man_com_key = man_com_key+":"+str(field_key)
                                        app.redis.lpush(list_com, list_man_com_key)
                                        app.redis.hset(man_com_key, field_key, json.dumps(obj, default=default))
                                        return { 'success': True }, 200
                elif(innings == 2):
                    # teamA is doing  mistake
                    if(penalty == 'teamA'):
                        if(row_last_record['penalty_a']):
                            pnlt_a = row_last_record['penalty_a'] + 5
                        else:
                            pnlt_a = 5
                        update_record= """
                                UPDATE PLAYERSCORECARD SET PENALTY_A = %s WHERE MATCH_ID = %s AND BALL_ID = %s
                        """
                        params = (pnlt_a, matchid, ballid)
                        updated_record = writeSQL(update_record, params)
                        if(updated_record):
                            query_playerscorecard= """
                            SELECT * FROM PLAYERSCORECARD WHERE MATCH_ID = %s AND INNINGS = %s ORDER BY ID desc limit 1
                            """
                            params = (matchid, innings)
                            row_lastrecord = readSQL(query_playerscorecard, params)
                            if(row_lastrecord):
                                pnlt = 0
                                if(row_last_record['ball_id'] == args['ballid']):
                                    pnlt = row_lastrecord['penalty_a']
                                else:
                                    if(row_last_record['penalty_a']):
                                        pnlt = row_last_record['penalty_a'] + 5
                                    else:
                                        pnlt = 5
                                teama_score = row_lastrecord['team_a_score']
                                teamb_score = row_lastrecord['team_b_score'] + 5
                                teamb_over = row_lastrecord['team_b_over']
                                balls = int(teamb_over) + (round(teamb_over % 1, 2) * 10 / 6)
                                cal_cur_rate = teamb_score / balls
                                remainingOvrs = float(formatOver) - float(teamb_over)
                                remainingBalls = int(remainingOvrs) + (round(remainingOvrs % 1, 2) * 10 / 6)
                                cal_req_rate = round((teama_score - teamb_score) / remainingBalls, 2)
                                get_curr_inng = app.redis.get("match:"+str(matchid)+":innings")
                                get_inng = json.loads(get_curr_inng)
                                curr_key = "livescorecard:"+str(matchid)+":current:"+str(get_inng)
                                curr_livecard = app.redis.get(curr_key)
                                key_info = json.loads(curr_livecard)
                                get_fullcard = "fullscorecard:"+str(matchid)+":"+str(innings)+":"+str(key_info['ball'])
                                fullcard = json.loads(app.redis.get(get_fullcard))
                                fullcard['teamBRuns'] = teamb_score
                                fullcard['curr_rate'] = round(cal_cur_rate, 2)
                                fullcard['req_rate'] = cal_req_rate
                                # print(fullcard)
                                for key, value in fullcard['innings_1'].items() :
                                    if key == 'extras':
                                        fullcard['innings_1']['extras']['pnlt'] = pnlt
                                updated_key = app.redis.set(get_fullcard, json.dumps(fullcard, default=default))
                                if updated_key:
                                    query_playerscorecard= """
                                    UPDATE PLAYERSCORECARD SET TEAM_B_SCORE = %s, CURR_RATE = %s, REQ_RATE = %s, PENALTY_A = %s WHERE ID = %s
                                    """
                                    params = (teamb_score, float(round(cal_cur_rate, 2)), cal_req_rate, pnlt, row_lastrecord['id'])
                                    updated_playerscorecard = writeSQL(query_playerscorecard, params)
                                    if updated_playerscorecard:
                                        #manual commentry
                                        list_com = "list:"+str(matchid)+":"+str(get_inng)
                                        man_com_key = "commentry:"+str(matchid)+":"+str(get_inng)+":manual"
                                        obj = {}
                                        obj['comment'] = args['message']
                                        obj['datetime'] = datetime.utcnow()
                                        if(app.redis.hkeys(man_com_key)):
                                            index_val = [val for loc, val in enumerate(app.redis.hkeys(man_com_key)) if math.floor(float(val)) == key_info['ball']]
                                            if(index_val):
                                                max_val = float(max(index_val))
                                                field_key = format(max_val + 0.1, ".1f")
                                            else:
                                                field_key = key_info['ball'] + 0.1
                                        else:
                                            field_key = key_info['ball'] + 0.1
                                        list_man_com_key = man_com_key+":"+str(field_key)
                                        app.redis.lpush(list_com, list_man_com_key)
                                        app.redis.hset(man_com_key, field_key, json.dumps(obj, default=default))
                                        return { 'success': True }, 200
                    # teamB is doing  mistake
                    elif(penalty == 'teamB'):
                        if(row_last_record['penalty_b']):
                            pnlt_b = row_last_record['penalty_b'] + 5
                        else:
                            pnlt_b = 5
                        update_record= """
                                UPDATE PLAYERSCORECARD SET PENALTY_B = %s WHERE MATCH_ID = %s AND BALL_ID = %s
                        """
                        params = (pnlt_b, matchid, ballid)
                        updated_record = writeSQL(update_record, params)
                        if(updated_record):
                            query_playerscorecard= """
                            SELECT * FROM PLAYERSCORECARD WHERE MATCH_ID = %s AND INNINGS = %s ORDER BY ID desc limit 1
                            """
                            params = (matchid, innings)
                            row_lastrecord = readSQL(query_playerscorecard, params)
                            if(row_lastrecord):
                                pnlt = 0
                                if(row_last_record['ball_id'] == args['ballid']):
                                    pnlt = row_lastrecord['penalty_b']
                                else:
                                    if(row_last_record['penalty_b']):
                                        pnlt = row_last_record['penalty_b'] + 5
                                    else:
                                        pnlt = 5
                                teama_score = row_lastrecord['team_a_score'] + 5
                                teamb_score = row_lastrecord['team_b_score'] 
                                teamb_over = row_lastrecord['team_b_over']
                                balls = int(teamb_over) + (round(teamb_over % 1, 2) * 10 / 6)
                                cal_cur_rate = teamb_score / balls
                                remainingOvrs = float(formatOver) - float(teamb_over)
                                remainingBalls = int(remainingOvrs) + (round(remainingOvrs % 1, 2) * 10 / 6)
                                cal_req_rate = round((teama_score - teamb_score) / remainingBalls, 2)
                                get_curr_inng = app.redis.get("match:"+str(matchid)+":innings")
                                get_inng = json.loads(get_curr_inng)
                                curr_key = "livescorecard:"+str(matchid)+":current:"+str(get_inng)
                                curr_livecard = app.redis.get(curr_key)
                                key_info = json.loads(curr_livecard)
                                get_fullcard = "fullscorecard:"+str(matchid)+":"+str(innings)+":"+str(key_info['ball'])
                                fullcard = json.loads(app.redis.get(get_fullcard))
                                fullcard['teamARuns'] = teama_score
                                fullcard['teamBRuns'] = teamb_score
                                fullcard['curr_rate'] = round(cal_cur_rate, 2)
                                fullcard['req_rate'] = cal_req_rate
                                for key, value in fullcard['innings_2'].items() :
                                    if key == 'extras':
                                        fullcard['innings_2']['extras']['pnlt'] = pnlt
                                updated_key = app.redis.set(get_fullcard, json.dumps(fullcard, default=default))
                                if updated_key:
                                    query_playerscorecard= """
                                    UPDATE PLAYERSCORECARD SET TEAM_A_SCORE = %s, CURR_RATE = %s, REQ_RATE = %s, PENALTY_B = %s WHERE ID = %s
                                    """
                                    params = (teama_score, float(round(cal_cur_rate, 2)), cal_req_rate, pnlt, row_lastrecord['id'])
                                    updated_playerscorecard = writeSQL(query_playerscorecard, params)
                                    if updated_playerscorecard:
                                        #manual commentry
                                        list_com = "list:"+str(matchid)+":"+str(get_inng)
                                        man_com_key = "commentry:"+str(matchid)+":"+str(get_inng)+":manual"
                                        obj = {}
                                        obj['comment'] = args['message']
                                        obj['datetime'] = datetime.utcnow()
                                        if(app.redis.hkeys(man_com_key)):
                                            index_val = [val for loc, val in enumerate(app.redis.hkeys(man_com_key)) if math.floor(float(val)) == key_info['ball']]
                                            if(index_val):
                                                max_val = float(max(index_val))
                                                field_key = format(max_val + 0.1, ".1f")
                                            else:
                                                field_key = key_info['ball'] + 0.1
                                        else:
                                            field_key = key_info['ball'] + 0.1
                                        list_man_com_key = man_com_key+":"+str(field_key)
                                        app.redis.lpush(list_com, list_man_com_key)
                                        app.redis.hset(man_com_key, field_key, json.dumps(obj, default=default))
                                        return { 'success': True }, 200
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500