from flask_restful import Resource, reqparse, request
from common.db import writeSQL, readSQL, readManySQL
import app, json
from common.util import default


class PitchChart(Resource):
    def get(self):
        try:
            args = request.args
            if 'bowler' in args:
                bowler = args['bowler']
                pitch_key = 'pitch:'+str(args['matchid'])+":"+str(args['innings'])
                response = app.redis.hget(pitch_key, bowler)
                if response:
                    loaded_val = json.loads(response)
                    return { 'success': True, 'data': loaded_val }, 200
                else:
                    return { 'success': False, 'message': 'data not found' }, 404
            else:
                return { 'success': False, 'message': 'missing required parameters' }, 400
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500