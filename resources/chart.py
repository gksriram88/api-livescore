from flask_restful import Resource, reqparse, request
from common.db import writeSQL, readSQL, readManySQL
import app, json
from common.util import default


class Chart(Resource):
    def get(self):
        try:
            args = request.args
            match_id = args['matchid']
            innings = args['innings']
            # current key formation
            # get inning
            # get_curr_inng = app.redis.get("match:"+str(args['matchid'])+":innings")
            # get_inng = json.loads(get_curr_inng)
            curr_key = "livescorecard:"+str(match_id)+":current:"+str(innings)
            curr_livecard = app.redis.get(curr_key)
            key_info = json.loads(curr_livecard)
            pipe = app.redis.pipeline()
            for i in range(1, key_info['ball'] + 1):
                    key = "commentry:"+str(match_id)+":"+str(innings)
                    pipe.hget(key, str(i))
            
            responses = [commentry_data for commentry_data in pipe.execute()]
            res = []
            for com_item in responses:
                if com_item:
                    res.append(json.loads(com_item))
            result = []
            wicket_fall = [] 
            method = []
            # innings_1 = []
            # innings_2 = []
            for comm in res:
                if comm['fallOfWickets']:
                    wicket_fall.append(comm['fallOfWickets'])
                if comm['method']:
                    method.append(comm['method'])
                if round(comm['over'] % 1, 2) == 0.6:
                    comm['fallOfWickets'] = wicket_fall
                    comm['method'] = method
                    result.append(comm)
                    wicket_fall = [] 
                    method = []
            return { 'success': True, 'data': result }, 200
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500