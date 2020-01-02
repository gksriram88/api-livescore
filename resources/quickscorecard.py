from flask_restful import Resource, reqparse, request
import app, json


class QuickScoreCard(Resource):
    def get(self):
        try:
            args = request.args
            match_id = args['match_id']
            get_curr_inng = app.redis.get("match:"+str(match_id)+":innings")
            if(get_curr_inng):
                get_inng = json.loads(get_curr_inng)
                # key formation
                key = "quickscorecard:"+str(match_id)+":current:"+str(get_inng)
                quick_key = json.loads(app.redis.get(key))
                val = quick_key['score']
                return { 'success': True, 'data': val }, 200
            else:
                return { 'success': False, 'message': 'no match found' }, 404
        except Exception as e:
            print(e)
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500
    
    def put(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('key', type=str, required=True, help="Key cannot be missing!", location='json')
        parser.add_argument('match_id', type=int, required=True, help="Match Id cannot be missing!", location='json')
        args = parser.parse_args()
        try:
            key_val = args['key']
            match_id = args['match_id']
            get_curr_inng = app.redis.get("match:"+str(match_id)+":innings")
            if(get_curr_inng):
                get_inng = json.loads(get_curr_inng)
                # key formation
                key = "quickscorecard:"+str(match_id)+":current:"+str(get_inng)
                quick_key = json.loads(app.redis.get(key))
                quick_key['score'] = key_val 
                app.redis.set(key, json.dumps(quick_key))
                live_key = "livescorecard:"+str(args['match_id'])+":current:"+str(get_inng)
                livecard_key = json.loads(app.redis.get(live_key))
                livecard_key['quickcard'] = key_val
                app.redis.set(live_key, json.dumps(livecard_key))
                return { 'success': True }, 200
            else:
                return { 'success': False, 'message': 'no match found' }, 404
        except Exception as e:
            print(e)
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500