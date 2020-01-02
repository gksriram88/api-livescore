from flask_restful import Resource, reqparse, request
from common.db import writeSQL, readSQL, readManySQL
import app, json
from common.util import default


class RadarChart(Resource):
    def get(self):
        try:
            args = request.args
            if 'striker_1' in args and 'striker_2' in args:
                striker_1 = args['striker_1']
                striker_2 = args['striker_2']
                radar_key = 'radar:'+str(args['matchid'])+":"+str(args['innings'])
                pipe = app.redis.pipeline()
                pipe.hget(radar_key, striker_1)
                pipe.hget(radar_key, striker_2)
                response = []
                for radar_data in pipe.execute():
                    if radar_data:
                        temp = []
                        load_res = json.loads(radar_data)
                        for key, val in load_res.items():
                            reg  = {}
                            reg['region'] = key
                            reg['runs'] = val
                            temp.append(reg)
                        response.append(temp)
                return { 'success': True, 'data': response }, 200
            else:
                return { 'success': False, 'message': 'missing required parameters' }, 400
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500