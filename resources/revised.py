from flask_restful import Resource, reqparse, request
from common.db import writeSQL, readSQL, readManySQL
import app, json, math
from common.util import default
from datetime import datetime


class Revised(Resource):
    def put(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('innings', type=int, required=True, help="innings cannot be missing!", location='json')
        parser.add_argument('match_id', type=str, required=True, help="match id of the match cannot be missing!", location='json')
        parser.add_argument('ballid', type=int, required=True, help="ball id cannot be missing!", location='json')
        parser.add_argument('rvs_a_target', type=str, required=True, help="penalty cannot be missing!", location='json')
        parser.add_argument('rvs_a_over', type=str, required=True, help="Format over cannot be missing!", location='json')
        parser.add_argument('rvs_b_over', type=str, required=True, help="Format over cannot be missing!", location='json')
        parser.add_argument('message', type=str, required=True, help="Message cannot be missing!", location='json')
        args = parser.parse_args()
        try:
            update_playerscorecard= """
            UPDATE PLAYERSCORECARD SET RVS_A_OVER = %s, RVS_B_OVER = %s, RVS_A_TARGET = %s WHERE MATCH_ID = %s AND INNINGS = %s AND BALL_ID = %s
            """
            params = (args['rvs_a_over'], args['rvs_b_over'], args['rvs_a_target'], args['match_id'], args['innings'], args['ballid'])
            updated_row = writeSQL(update_playerscorecard, params)
            if updated_row:
                get_fullcard = "fullscorecard:"+str(args['match_id'])+":"+str(args['innings'])+":"+str(args['ballid'])
                print(get_fullcard)
                fullcard = json.loads(app.redis.get(get_fullcard))
                fullcard['rvs_a_target'] = args['rvs_a_target']
                fullcard['rvs_a_over'] = args['rvs_a_over']
                fullcard['rvs_b_over'] = args['rvs_b_over']
                app.redis.set(get_fullcard, json.dumps(fullcard))
                #manual commentry
                list_com = "list:"+str(args['match_id'])+":"+str(args['innings'])
                man_com_key = "commentry:"+str(args['match_id'])+":"+str(args['innings'])+":manual"
                obj = {}
                obj['comment'] = args['message']
                obj['datetime'] = datetime.utcnow()
                if(app.redis.hkeys(man_com_key)):
                    index_val = [val for loc, val in enumerate(app.redis.hkeys(man_com_key)) if math.floor(float(val)) == args['ballid']]
                    if(index_val):
                        max_val = float(max(index_val))
                        field_key = format(max_val + 0.1, ".1f")
                    else:
                        field_key = args['ballid'] + 0.1
                else:
                    field_key = args['ballid'] + 0.1
                list_man_com_key = man_com_key+":"+str(field_key)
                app.redis.lpush(list_com, list_man_com_key)
                app.redis.hset(man_com_key, field_key, json.dumps(obj, default=default))
                return { 'success': True }, 200
            else:
                return { 'success': False, 'message': 'no match found' }, 404
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500