import app
from flask_restful import Resource, reqparse, request
from common.db import writeSQL, readSQL, readManySQL

class Country(Resource):
    def get(self):
        try:
            args = request.args
            if 'id' in args:
                query= """
                        SELECT * FROM COUNTRY WHERE ID = %s
                        """
                params = (args['id'],)
                countries = readSQL(query, params)
            else:
                query= """
                        SELECT * FROM COUNTRY
                        """
                countries = readManySQL(query, None)
            if countries:
                return { 'success' : True, 'data':  countries}, 200
            else:
                return {'sucess' : False, 'message': 'no records found' }, 404        
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500

    def post(self):
        try:
            parser = reqparse.RequestParser(bundle_errors=True)
            parser.add_argument('name', type=str, required=True, help="Name of the country cannot be missing!", location='json')
            parser.add_argument('code', type=str, required=True, help="Short Code cannot be missing!", location='json')
            parser.add_argument('status', type=str, required=True, help="Status cannot be missing!", location='json')
            args = parser.parse_args()
            query_insert= """
                INSERT INTO COUNTRY (NAME,CODE,STATUS) 
                VALUES
                (%s, %s, %s)
            """
            params = (args['name'], args['code'], args['status'])
            countries = writeSQL(query_insert, params)
            if countries:
                return { 'success' : True, 'message': 'Successfully created'}, 200
            else:
                return {'sucess' : False }, 400        
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500

    def put(self):
        try:
            parser = reqparse.RequestParser(bundle_errors=True)
            parser.add_argument('name', type=str, required=True, help="Name of the country cannot be missing!", location='json')
            parser.add_argument('code', type=str, required=True, help="Short Code cannot be missing!", location='json')
            parser.add_argument('status', type=str, required=True, help="Status cannot be missing!", location='json')
            parser.add_argument('id', type=str, required=True, help="id cannot be missing!", location='json')
            args = parser.parse_args()
            query_insert= """
                UPDATE COUNTRY SET NAME = %s, CODE = %s, STATUS = %s WHERE ID = %s
            """
            params = (args['name'], args['code'], args['status'], args['id'])
            countries = writeSQL(query_insert, params)
            if countries:
                return { 'success' : True, 'message': 'Updated successfully'}, 200
            else:
                return {'sucess' : False }, 400        
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500
            