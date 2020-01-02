from flask_restful import Resource, reqparse
from common.db import writeSQL, readSQL
from common.util import default
import app, json


class LiveScoreByBall(Resource):
    @app.jwt_required
    def get(self, livescorecard_id):
        try:
            if livescorecard_id:
                prev_id = int(livescorecard_id) - 1
                if prev_id:
                    query_playerscorecard= """
                    SELECT * FROM PLAYERSCORECARD WHERE ID = %s
                    """
                    params = (prev_id,)
                    print(prev_id)
                    row_playerscorecard = readSQL(query_playerscorecard, params)
                    data = json.dumps({'success' : True, 'card': row_playerscorecard}, default=default)
                    return json.loads(data), 200
            else:
                return {'success': False}, 404        
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500
            
        