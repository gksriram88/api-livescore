import app
from flask_restful import Resource, reqparse, request
from common.db import writeSQL, readSQL, readManySQL

class Team(Resource):
    def get(self):
        try:
            args = request.args
            if 'id' in args:
                query= """
                        SELECT * FROM TEAM WHERE ID = %s
                        """
                params = (args['id'],)
                teams = readSQL(query, params)
            else:
                query= """
                        SELECT * FROM TEAM
                        """
                teams = readManySQL(query, None)
            if teams:
                return { 'success' : True, 'data':  teams}, 200
            else:
                return {'sucess' : False, 'message': 'no records found' }, 404        
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500

    def post(self):
        try:
            parser = reqparse.RequestParser(bundle_errors=True)
            parser.add_argument('name', type=str, required=True, help="Name of the team cannot be missing!", location='json')
            parser.add_argument('logo', type=str, required=True, help="Logo cannot be missing!", location='json')
            parser.add_argument('shortname', type=str, required=True, help="Short name cannot be missing!", location='json')
            parser.add_argument('country', type=str, required=True, help="Country cannot be missing!", location='json')
            parser.add_argument('status', type=str, required=True, help="Status cannot be missing!", location='json')
            args = parser.parse_args()
            query_insert= """
                INSERT INTO TEAM (NAME, LOGO, SHORTNAME, C_ID, STATUS) 
                VALUES
                (%s, %s, %s, %s, %s)
            """
            params = (args['name'], args['logo'], args['shortname'], args['country'], args['status'])
            teams = writeSQL(query_insert, params)
            if teams:
                return { 'success' : True, 'message': 'Successfully created'}, 200
            else:
                return {'sucess' : False }, 400        
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500

    def put(self):
        try:
            parser = reqparse.RequestParser(bundle_errors=True)
            parser.add_argument('name', type=str, required=True, help="Name of the team cannot be missing!", location='json')
            parser.add_argument('logo', type=str, required=True, help="Logo cannot be missing!", location='json')
            parser.add_argument('shortname', type=str, required=True, help="Short name cannot be missing!", location='json')
            parser.add_argument('country', type=str, required=True, help="Country cannot be missing!", location='json')
            parser.add_argument('status', type=str, required=True, help="Status cannot be missing!", location='json')
            parser.add_argument('id', type=str, required=True, help="id cannot be missing!", location='json')
            args = parser.parse_args()
            query_insert= """
                UPDATE TEAM SET NAME = %s, LOGO = %s, SHORTNAME = %s, C_ID = %s, STATUS = %s WHERE ID = %s
            """
            params = (args['name'], args['logo'], args['shortname'], args['country'], args['status'], args['id'])
            teams = writeSQL(query_insert, params)
            if teams:
                return { 'success' : True, 'message': 'Updated successfully'}, 200
            else:
                return {'sucess' : False }, 400        
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500
            