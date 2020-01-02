from flask_restful import Resource, reqparse, request
from common.db import readManySQL
import app, json
from common.util import default, getDatetime


class Points(Resource):
    @app.jwt_required
    def get(self):
        try:
            args = request.args
            if 'id' in args:
                query_points = """
                    SELECT POINTS.G_NAME, POINTS.PLAYED, POINTS.WON, POINTS.LOST, POINTS.NR, POINTS.NRR, TEAM.NAME FROM MATCHTYPE
                    JOIN POINTS ON MATCHTYPE.G_ID = POINTS.G_ID
                    JOIN TEAM ON POINTS.TEAM_ID = TEAM.ID
                    WHERE MATCHTYPE.ID = %s
                """
                params = (args['id'],)
                points = readManySQL(query_points, params)
                if points:
                    data = json.dumps({'success' : True, 'data': points}, default=default)
                    return json.loads(data), 200
                else:
                    return {'success': False, 'message': 'No points found' }, 404
            else:
                return {'success': False, 'message': 'missing parameters' }, 400
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500
