import app, json
from flask_restful import Resource, reqparse, request
from common.db import writeSQL, readSQL, readManySQL
from common.util import default

class MatchList(Resource):
    def get(self):
        try:
            args = request.args
            row_match = ''
            if 'status' in args and args['status'] == 'LIVE':
                query_match= """
                        select match.id, match.name, date, teama.name as teama, teamb.name as teamb, teama.logo as teama_logo, teamb.logo as teamb_logo, matchtype.name, match."date", match.venue  from "match"
                        join team as teama on teama.id = match.team_a 
                        join team as teamb on teamb.id = match.team_b
                        join matchtype on matchtype.id = match.matchtype_id
                        where match.status = %s
                        """
                params = (args['status'],)
                row_match = readManySQL(query_match, params)
            elif 'status' in args and args['status'] == 'UPCOMING':
                query_match= """
                        select match.id, match.name, date, teama.name as teama, teamb.name as teamb, teama.logo as teama_logo, teamb.logo as teamb_logo, matchtype.name, match."date", match.venue  from "match"
                        join team as teama on teama.id = match.team_a 
                        join team as teamb on teamb.id = match.team_b
                        join matchtype on matchtype.id = match.matchtype_id
                        where match.status = %s
                        """
                params = (args['status'],)
                row_match = readManySQL(query_match, params)
            elif 'status' in args and args['status'] == 'PAST':
                query_match= """
                        select match.id, match.name, date, teama.name as teama, teamb.name as teamb, teama.logo as teama_logo, teamb.logo as teamb_logo, matchtype.name, match."date", match.venue  from "match"
                        join team as teama on teama.id = match.team_a 
                        join team as teamb on teamb.id = match.team_b
                        join matchtype on matchtype.id = match.matchtype_id
                        where match.status = %s
                        """
                params = (args['status'],)
                row_match = readManySQL(query_match, params)
            if row_match and len(row_match) > 0:
                data = json.dumps({'success' : True, 'data': row_match}, default=default)
                return json.loads(data), 200
            else:
                return {'success': False, 'error': 'Data not found'}, 200
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500
    