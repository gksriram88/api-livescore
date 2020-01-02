from flask_restful import Resource, reqparse, request
from common.db import writeSQL, readSQL, readManySQL
import app, json,math
from common.util import default
from datetime import datetime

class ManualCommentry(Resource):
    @app.jwt_required
    def get(self,matchid):
        try:
            args = request.args
            get_curr_inng = app.redis.get("match:"+matchid+":innings")
            get_inng = json.loads(get_curr_inng)
            list_commentry2={}
            if get_inng == 2 :
                key_name = "commentry:"+matchid+":1:manual"
                list_commentry = app.redis.hgetall(key_name)
                key_name2 = "commentry:"+matchid+":2:manual"
                list_commentry2 = app.redis.hgetall(key_name2)
            else:
                key_name = "commentry:"+matchid+":"+str(get_inng)+":manual"
                list_commentry = app.redis.hgetall(key_name)
            data = []
            obj={}
            for key, val in list_commentry.items():
                obj=json.loads(val)
                obj['key']=key
                obj['innings']=1
                data.append(obj)
            for key, val in list_commentry2.items():
                obj=json.loads(val)
                obj['key']=key
                obj['innings']=2
                data.append(obj)
            return {'success': True, 'data': data}, 200
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500

    @app.jwt_required
    def put(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('match_id', type=str, required=True, help="Match id cannot be missing!", location='json')
        parser.add_argument('key', type=str, required=True, help="key of the comment cannot be missing!", location='json')
        parser.add_argument('commentry', type=str, required=True, help="Commentry cannot be missing!", location='json')
        parser.add_argument('innings', type=str, required=True, help="innings cannot be missing!", location='json')
        args = parser.parse_args()
        try:
            key_name ="commentry:"+str(args['match_id'])+":"+str(args['innings'])+":manual"
            field_key = str(args['key'])
            hash_val = json.loads(app.redis.hget(key_name, field_key))
            if hash_val:
                hash_val['comment'] = args['commentry']
                app.redis.hset(key_name, field_key, json.dumps(hash_val))
                return {'success': True, 'message': 'updated successfully'}
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500

    @app.jwt_required
    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('match_id', type=str, required=True, help="Match id cannot be missing!", location='json')
        parser.add_argument('commentry', type=str, required=True, help="Commentry cannot be missing!", location='json')
        args = parser.parse_args()
        try:
            get_curr_inng = app.redis.get("match:"+str(args['match_id'])+":innings")
            get_inng = json.loads(get_curr_inng)
            curr_key = "livescorecard:"+str(args['match_id'])+":current:"+str(get_inng)
            curr_livecard = app.redis.get(curr_key)
            key_info = json.loads(curr_livecard)
            list_com = "list:"+str(args['match_id'])+":"+str(get_inng)
            man_com_key = "commentry:"+str(args['match_id'])+":"+str(get_inng)+":manual"
            obj = {}
            obj['comment'] = args['commentry']
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
            return {'success': True, 'message': 'added successfully'}
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500

    @app.jwt_required
    def delete(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('match_id', type=str, required=True, help="Match id cannot be missing!", location='json')
        parser.add_argument('key', type=str, required=True, help="key of the comment cannot be missing!", location='json')
        parser.add_argument('innings', type=int, required=True, help="innings cannot be missing!", location='json')
        args = parser.parse_args()
        try:
            get_inng=args['innings']
            com_key = "list:"+str(args['match_id'])+":"+str(get_inng)
            hkey= "commentry:"+str(args['match_id'])+":"+str(get_inng)+":manual"
            get_list = app.redis.lrange(com_key, 0, -1)
            count_len = app.redis.llen(com_key) - 3
            for key in get_list:
                actual_key = key
                splited_key = key.split(':')
                if splited_key[3] == 'manual' and splited_key[4]== str(args['key']):
                    app.redis.lrem(com_key, count_len, actual_key)
                    app.redis.hdel(hkey,splited_key[4])
            return {'success': True, 'message': 'delete successfully'}
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500
    