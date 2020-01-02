from flask_restful import Resource, reqparse, request
from common.db import writeSQL, readSQL, readManySQL
import app, json, math


class Undo(Resource):
    @app.jwt_required
    def get(self):
        try:
            args = request.args
            get_curr_inng = app.redis.get("match:"+str(args['matchid'])+":innings")
            get_inng = json.loads(get_curr_inng)
            # postgres db
            query_playerscorecard= """
            SELECT * FROM PLAYERSCORECARD WHERE MATCH_ID = %s AND INNINGS = %s ORDER BY ID desc limit 1
            """
            params = (args['matchid'], get_inng)
            row_playerscorecard = readSQL(query_playerscorecard, params)
            if row_playerscorecard:
                del_playerscorecard= """
                    DELETE FROM PLAYERSCORECARD WHERE ID = %s
                """
                params = (row_playerscorecard['id'],)
                del_record = writeSQL(del_playerscorecard, params)
                prv_playerscorecard="""
                    SELECT * FROM PLAYERSCORECARD WHERE ID = %s AND MATCH_ID = %s
                """
                prv_id = row_playerscorecard['id'] - 1
                params = (prv_id, args['matchid'])
                prv_record = readSQL(prv_playerscorecard, params)
                # ball_id = prv_playerscorecard['ball_id']
                if prv_record and 'team_a_over' in prv_record and 'team_b_over' in prv_record:
                    team_a_over = prv_record['team_a_over']
                    team_b_over = prv_record['team_b_over']
                else:
                    team_a_over = "0.0"
                    team_b_over = "0.0"
                if del_record:
                    #redis
                    if get_inng == 1:
                        over = team_a_over
                    else:
                        over = team_b_over
                    curr_key = "livescorecard:"+str(args['matchid'])+":current:"+str(get_inng)
                    com_key = "list:"+str(args['matchid'])+":"+str(get_inng)
                    curr_livecard = app.redis.get(curr_key)
                    key_info = json.loads(curr_livecard)
                    get_list = app.redis.lrange(com_key, 0, -1)
                    count_len = app.redis.llen(com_key) - 3
                    for key in get_list:
                        actual_key = key
                        splited_key = key.split(':')
                        if(splited_key[3] == 'manual' and math.floor(float(splited_key[4])) == key_info['ball']):
                            app.redis.lrem(com_key, count_len, actual_key)
                        elif(splited_key[3].isdigit() and math.floor(float(splited_key[3])) == key_info['ball']):
                            app.redis.lrem(com_key, count_len, actual_key)
                        count_len = count_len - 1
                    key_info['over'] = str(over)
                    key_info['ball'] = key_info['ball'] - 1
                    app.redis.set(curr_key, json.dumps(key_info))
                    return {'success': True, 'message': 'sucessfully deleted the last record' }, 200
            else:
                return {'success': False, 'message': 'no record to delete' }, 200
        except Exception as e:
            print(e)
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500