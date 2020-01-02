import app
from flask_restful import Resource, reqparse
from common.db import writeSQL

class Register(Resource):
    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('name', type=str, required=True, help="Name cannot be blank!", location='json')
        parser.add_argument('username', type=str, required=True, help="Username cannot be blank!", location='json')
        parser.add_argument('password', type=str, required=True, help="password cannot be blank!", location='json')
        args = parser.parse_args()
        try:
            if args and ('name' in args and 'username' in args and 'password' in args):
                name = args['name']
                username = args['username']
                password = args['password']
                if not (username is None and password is None):
                    query= """
                            INSERT INTO USERS (NAME, USERNAME, PASSWORD) 
                            VALUES
                            (%s, %s, %s)
                            """
                    hashed_password = app.bcrypt.generate_password_hash(password.encode('utf-8'))
                    params = (name, username, hashed_password.decode('utf8'))
                    count = writeSQL(query, params)
                    if count:
                        return { 'success' : True }, 200
            else:
                return {'sucess' : False }, 400        
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500
            