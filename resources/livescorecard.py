from flask_restful import Resource, reqparse, request
import app, json


class LiveScoreCard(Resource):
    def get(self):
        try:
            args = request.args
            innings = args['innings']
            ball_id = args['ballid']
            match_id = args['matchid']

            # key formation
            key = "livescorecard:"+str(match_id)+":"+str(innings)+":"+str(ball_id)
            # current key formation
            curr_key = "livescorecard:"+str(match_id)+":current"


            livecard = app.redis.get(key)
            curr_livecard = app.redis.get(curr_key)
            result = { 'livecard': json.loads(livecard), 'current': json.loads(curr_livecard) }
            return { 'success': True, 'data': result }, 200
        except Exception as e:
            print(e)
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500