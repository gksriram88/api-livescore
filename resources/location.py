import app
from flask_restful import Resource, reqparse, request, abort
from common.db import writeSQL, readSQL, readManySQL

class Location(Resource):
    def get(self):
        try:
            args = request.args
            if 'id' in args:
                query= """
                        SELECT * FROM LOCATION WHERE ID = %s
                        """
                params = (args['id'],)
                locations = readSQL(query, params)
            elif 'countryid' in args:
                query= """
                        SELECT * FROM LOCATION WHERE C_ID = %s
                        """
                params = (args['countryid'],)
                locations = readManySQL(query, params)
            else:
                return {'sucess' : False, 'message': 'missing parameters' }, 400  
            if locations:
                return { 'success' : True, 'data':  locations}, 200
            else:
                return {'sucess' : False, 'message': 'no records found' }, 404        
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500

    def post(self):
        try:
            parser = reqparse.RequestParser(bundle_errors=True)
            parser.add_argument('venue', type=str, required=True, help="Name of the venue cannot be missing!", location='json')
            parser.add_argument('status', type=str, required=True, help="Status cannot be missing!", location='json')
            parser.add_argument('countryid', type=str, required=True, help="Country cannot be missing!", location='json')
            args = parser.parse_args()
            query_insert= """
                INSERT INTO LOCATION (VENUE, STATUS, C_ID) 
                VALUES
                (%s, %s, %s)
            """
            params = (args['venue'], args['status'], args['countryid'])
            location = writeSQL(query_insert, params)
            if location:
                return { 'success' : True, 'message': 'Successfully created'}, 200
            else:
                return {'sucess' : False }, 400        
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500


    def put(self):
        try:
            parser = reqparse.RequestParser(bundle_errors=True)
            parser.add_argument('venue', type=str, required=True, help="Name of the venue cannot be missing!", location='json')
            parser.add_argument('status', type=str, required=True, help="Status cannot be missing!", location='json')
            parser.add_argument('countryid', type=str, required=True, help="Country cannot be missing!", location='json')
            parser.add_argument('id', type=str, required=True, help="id cannot be missing!", location='json')
            args = parser.parse_args()
            query_insert= """
                UPDATE LOCATION SET VENUE = %s, STATUS = %s, C_ID = %s  WHERE ID = %s
            """
            params = (args['venue'], args['status'], args['countryid'], args['id'])
            location = writeSQL(query_insert, params)
            if location:
                return { 'success' : True, 'message': 'Updated successfully'}, 200
            else:
                return {'sucess' : False }, 400        
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500