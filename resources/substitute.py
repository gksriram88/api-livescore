from flask_restful import Resource, reqparse, request
from common.db import writeSQL, readSQL, readManySQL
import app, json, math
from common.util import default
from datetime import datetime


class Substitute(Resource):
    def put(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('match_id', type=int, required=True, help="match id cannot be missing!", location='json')
        parser.add_argument('player_sub', type=int, required=True, help="Substitute player cannot be missing!", location='json')
        parser.add_argument('player_main', type=int, required=True, help="Main Player cannot be missing!", location='json')
        parser.add_argument('message', type=str, required=True, help="Message cannot be missing!", location='json')
        args = parser.parse_args()
        try:
            match_id = args['match_id']
            get_curr_inng = app.redis.get("match:"+str(args['match_id'])+":innings")
            get_inng = json.loads(get_curr_inng)
            curr_key = "livescorecard:"+str(match_id)+":current:"+str(get_inng)
            curr_livecard = app.redis.get(curr_key)
            key_info = json.loads(curr_livecard)
            #db update
            query_squad= """
                SELECT * FROM SQUAD WHERE ID = (SELECT SQUAD_ID FROM MATCH WHERE ID = %s)
            """
            params = (args['match_id'],)
            row_squad = readSQL(query_squad, params)
            if row_squad:
                # main player update
                update_teamsquad_main= """
                        update teamsquad set player_in = False where (t_id_1 = %s or t_id_2 = %s) and player_id  = %s
                    """
                params = (row_squad['team_squad_1'], row_squad['team_squad_2'], args['player_main'])
                update_main = writeSQL(update_teamsquad_main, params)
                # sub player update
                update_teamsquad_sub= """
                        update teamsquad set player_in = True where (t_id_1 = %s or t_id_2 = %s) and player_id  = %s
                    """
                params = (row_squad['team_squad_1'], row_squad['team_squad_2'], args['player_sub'])
                update_sub = writeSQL(update_teamsquad_sub, params)
                if(update_main and update_sub):
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
                    return { 'success': False, 'message': 'player(s) not found' }, 404
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500