from flask_restful import Resource, reqparse, request
import app, json

class LiveStatus(Resource):
    def get(self):
        try:
            args = request.args
            match_id = args['match_id']
            # current key formation
            # get inning
            get_curr_inng = app.redis.get("match:"+str(args['match_id'])+":innings")
            get_inng = json.loads(get_curr_inng)
            curr_key = "livescorecard:"+str(match_id)+":current:"+str(get_inng)
            curr_livecard = app.redis.get(curr_key)
            key_info = json.loads(curr_livecard)
            result = { 'current': key_info}
            return { 'success': True, 'data': result }, 200
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500
    
    def put(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('match_id', type=int, required=True, help="Match id cannot be missing!", location='json')
        parser.add_argument('match_status', type=str, required=True, help="Status cannot be missing!", location='json')
        #validation
        args = parser.parse_args()
        try:
            get_curr_inng = app.redis.get("match:"+str(args['match_id'])+":innings")
            get_inng = json.loads(get_curr_inng)
            curr_key = "livescorecard:"+str(args['match_id'])+":current:"+str(get_inng)
            curr_livecard = json.loads(app.redis.get(curr_key))
            curr_livecard['match_status'] = args['match_status']
            app.redis.set(curr_key, json.dumps(curr_livecard))
            return { 'success': True, 'message': 'updated successfully' }, 200
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500