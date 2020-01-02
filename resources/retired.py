from flask_restful import Resource, reqparse, request
from common.db import writeSQL, readSQL, readManySQL
import app, json, math
from common.util import default
from datetime import datetime


class Retired(Resource):
    def put(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('match_id', type=int, required=True, help="match id cannot be missing!", location='json')
        parser.add_argument('player_id', type=int, required=True, help="player id cannot be missing!", location='json')
        parser.add_argument('message', type=str, required=True, help="message cannot be missing!", location='json')
        parser.add_argument('type', type=str, required=True, help="type cannot be missing!", location='json')
        args = parser.parse_args()
        try:
            match_id = args['match_id']
            get_curr_inng = app.redis.get("match:"+str(args['match_id'])+":innings")
            get_inng = json.loads(get_curr_inng)
            curr_key = "livescorecard:"+str(match_id)+":current:"+str(get_inng)
            curr_livecard = app.redis.get(curr_key)
            key_info = json.loads(curr_livecard)
            if (args['type'] == 'batsman'):
                get_fullcard = "fullscorecard:"+str(args['match_id'])+":"+str(get_inng)+":"+str(key_info['ball'])
                fullcard = json.loads(app.redis.get(get_fullcard))
                if get_inng == 1:
                    key = "innings_1"
                    player = str(args['player_id'])+"_pname"
                elif get_inng == 2:
                    key = "innings_2"
                    player = str(args['player_id'])+"_pname"
                if player in fullcard[key]['batting']:
                    player_record = fullcard[key]['batting'][player]
                    fullcard[key]['batting'][player]['status'] = 'retrd'
                    fullcard[key]['yetToBat'].append(player_record['name'])
                    fullcard_key = "fullscorecard:"+str(args['match_id'])+":"+str(get_inng)+":"+str(key_info['ball'])
                    app.redis.set(fullcard_key, json.dumps(fullcard))
                    query_playerscorecard= """
                        SELECT * FROM PLAYERSCORECARD WHERE MATCH_ID = %s AND INNINGS = %s ORDER BY ID desc limit 1
                        """
                    params = (args['match_id'], get_inng)
                    row_playerscorecard = readSQL(query_playerscorecard, params)
                    if row_playerscorecard:
                        update_playerscorecard= """
                        UPDATE PLAYERSCORECARD SET RETIRED = %s WHERE ID = %s
                        """
                        params = (int(args['player_id']), row_playerscorecard['id'])
                        updated_row = writeSQL(update_playerscorecard, params)
                        if updated_row:
                            #manual commentry
                            list_com = "list:"+str(match_id)+":"+str(get_inng)
                            man_com_key = "commentry:"+str(match_id)+":"+str(get_inng)+":manual"
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
            elif(args['type'] == 'bowler'):
                #manual commentry
                list_com = "list:"+str(match_id)+":"+str(get_inng)
                man_com_key = "commentry:"+str(match_id)+":"+str(get_inng)+":manual"
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
            else:
                return { 'success': False, 'message': 'no player found' }, 404
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500