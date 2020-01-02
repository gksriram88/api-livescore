from flask_restful import Resource, reqparse
import app, json


class MatchSquad(Resource):
    @app.jwt_required
    def get(self):
        squads = app.redis.get("matchsquad:44").decode('utf8')
        # curr_fullcard = app.redis.get("fullscorecard:44:1:current").decode('utf-8')
        return { 'success': True, 'squads': json.loads(squads) }, 200