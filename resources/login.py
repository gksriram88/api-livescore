from flask_restful import Resource, reqparse
from common.db import readSQL
import app

class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('username', type=str, required=True, help="Username cannot be blank!", location='json')
        parser.add_argument('password', type=str, required=True, help="password cannot be blank!", location='json')
        args = parser.parse_args()
        try:
            if args['username'] and args['password'] is not None:
                username = args['username']
                password = args['password']
                if username and password is not None:
                    query_user= """
                        SELECT PASSWORD FROM USERS WHERE USERNAME = %s
                        """
                    params = (username,)
                    row = readSQL(query_user, params)
                    status = app.bcrypt.check_password_hash(row['password'], password)
                    if status:
                        access_token = app.create_access_token(identity=username)
                        return { 'success' : True, 'token': access_token }, 200
                    else:
                        return { 'success' : False }, 404
            else:
                return { 'success' : False }, 400
                            
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500
            