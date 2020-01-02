from flask_restful import Resource, reqparse, request
import app, json


class Squad(Resource):
    @app.jwt_required
    def get(self):
        try:
            args = request.args
            innings = args['innings']
            squad_type = args['type']
            match_id = args['matchid']
            ball_id = args['ballid']

            # key formation
            key = "fullscorecard:"+str(match_id)+":"+str(innings)+":"+str(ball_id)

            result = app.redis.get(key)
            if result:
                obj = json.loads(result)
                if squad_type == 'batting' and int(innings) == 1:
                    obj = obj['innings_1']['batting']
                elif squad_type == 'batting' and int(innings) == 2:
                    obj = obj['innings_2']['batting']
                elif squad_type == 'bowling' and int(innings) == 1:
                    obj = obj['innings_1']['Bowling']
                elif squad_type == 'bowling' and int(innings) == 2:
                    obj = obj['innings_2']['Bowling']
                return { 'success': True, 'data': obj }, 200
            else:
                return { 'success': False, 'data': 'data not found' }, 404
        except Exception as e:
            print(e)
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500