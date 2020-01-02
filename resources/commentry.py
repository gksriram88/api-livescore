from flask_restful import Resource, reqparse, request
from common.db import writeSQL, readSQL, readManySQL
import app, json
from common.util import default


class Commentry(Resource):
    @app.jwt_required
    def get(self):
        try:
            args = request.args
            key_name = "commentry:"+str(args['id'])+":"+str(args['innings'])
            field_key = str(args['ball'])
            hash_key = app.redis.hget(key_name, field_key)
            if hash_key:
                data = json.dumps({'success' : True, 'data': json.loads(hash_key)}, default=default)
                return json.loads(data), 200
            else:
                return {'succes': False, 'message': 'no data found'}, 404
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500

    @app.jwt_required
    def put(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('match_id', type=int, required=True, help="Match id cannot be missing!", location='json')
        parser.add_argument('ball_id', type=int, required=True, help="Ball id of the comment cannot be missing!", location='json')
        parser.add_argument('commentry', type=str, required=True, help="Commentry cannot be missing!", location='json')
        parser.add_argument('innings', type=str, required=True, help="Innings cannot be missing!", location='json')
        #validation
        args = parser.parse_args()
        try:
            # get_curr_inng = app.redis.get("match:"+str(args['match_id'])+":innings")
            get_inng = args['innings']
            key_name = "commentry:"+str(args['match_id'])+":"+str(get_inng)
            field_key = str(args['ball_id'])
            hash_val = json.loads(app.redis.hget(key_name, field_key))
            if hash_val:
                hash_val['comment'] = args['commentry']
                app.redis.hset(key_name, field_key, json.dumps(hash_val))
                return {'success': True, 'message': 'updated successfully'}
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500