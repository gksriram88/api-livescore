from flask_restful import Resource, reqparse,request
from common.db import writeSQL, readSQL, readManySQL
import app, json
from common.util import default, getDatetime


class MatchType(Resource):
    @app.jwt_required
    def get(self):
        try:
            args = request.args
            if 'id' in args:
                query= """
                        SELECT * FROM MATCHTYPE WHERE ID = %s
                        """
                params = (args['id'],)
                series = readSQL(query, params)
            elif 'offset' in args and 'limit' in args:
                offset = int(request.args['offset'])
                limit = int(request.args['limit'])
                query= """
                        SELECT * FROM MATCHTYPE LIMIT %s OFFSET %s
                        """
                params = (limit, offset)     
                series = readManySQL(query, params)
            else:
                return {'sucess' : False, 'message': 'missing parameters' }, 400  
            if series:
                data = json.dumps({'success' : True, 'data': series}, default=default)
                return json.loads(data), 200
            else:
                return {'sucess' : False, 'message': 'no records found' }, 404        
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500

    @app.jwt_required
    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('name', type=str, required=True, help="Name of the match cannot be missing!", location='json')
        parser.add_argument('type', type=str, required=True, help="Type cannot be missing!", location='json')
        parser.add_argument('startdate', type=str, required=True, help="Start date cannot be missing!", location='json')
        parser.add_argument('enddate', type=str, required=True, help="End date cannot be missing!", location='json')
        parser.add_argument('venue', type=str, required=True, help="Venue cannot be missing!", location='json')
        parser.add_argument('created', type=str, required=True, help="Created date cannot be missing!", location='json')
        parser.add_argument('modified', type=str, required=True, help="Modified date cannot be missing!", location='json')
        parser.add_argument('teams', type=list, required=True, help="Modified date cannot be missing!", location='json')
        args = parser.parse_args()
        
        try:
            query_matchtype= """
                SELECT G_ID FROM MATCHTYPE ORDER BY ID DESC LIMIT 1
            """
            row_grp_id = readSQL(query_matchtype, None)
            if row_grp_id:
                if(row_grp_id['g_id']):
                    grp_id = row_grp_id['g_id'] + 1
                else:
                    grp_id = 1
                insert_matchtype= """
                    INSERT INTO MATCHTYPE (NAME, TYPE, START_DATE, END_DATE, G_ID, VENUE, CREATED, MODIFIED) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (args['name'], args['type'], args['startdate'], args['enddate'], grp_id, args['venue'], args['created'], args['modified'])
                write_matchtype = writeSQL(insert_matchtype, params)
                if write_matchtype:
                    for team in args['teams']:
                        insert_points= """
                            INSERT INTO POINTS (TEAM_ID, G_ID, CREATED, MODIFIED) 
                            VALUES (%s, %s, %s, %s)
                        """
                        params = (team, grp_id, getDatetime(), getDatetime())
                        writeSQL(insert_points, params)
                    return {'success': 'true', 'message': 'match type created'}, 200
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500
        