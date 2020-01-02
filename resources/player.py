import app, json
from flask_restful import Resource, reqparse, request, abort
from common.db import writeSQL, readSQL, readManySQL, writeFetchSQL
from common.util import default

class Player(Resource):
    def get(self):
        try:
            args = request.args
            if 'id' in args:
                query= """
                        SELECT * FROM PLAYER WHERE ID = %s
                        """
                params = (args['id'],)
                players = readSQL(query, params)
            elif 'teamid' in args:
                query= """
                        SELECT p1.*, t1.NAME as "team_name" FROM PLAYER p1 left join TEAM t1 on p1.team_id=t1.id  WHERE p1.TEAM_ID =%s
                        """
                params = (args['teamid'],)
                players = readManySQL(query, params)
            elif 'offset' in args and 'limit' in args:
                offset = int(request.args['offset'])
                limit = int(request.args['limit'])
                query= """
                        SELECT * FROM PLAYER LIMIT %s OFFSET %s
                        """
                params = (limit, offset)     
                players = readManySQL(query, params)
            else:
                return {'sucess' : False, 'message': 'missing parameters' }, 400  
            if players:
                data = json.dumps({'success' : True, 'data': players}, default=default)
                return json.loads(data), 200
            else:
                return {'sucess' : False, 'message': 'no records found' }, 404        
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500

    def post(self):
        try:
            parser = reqparse.RequestParser(bundle_errors=True)
            parser.add_argument('name', type=str, required=True, help="Name of the Player cannot be missing!", location='json')
            parser.add_argument('first_name', type=str, required=True, help="First name of the player cannot be missing!", location='json')
            parser.add_argument('last_name', type=str, required=True, help="Last name of the player cannot be missing!", location='json')
            parser.add_argument('batting_style', type=str, required=True, help="Batting style cannot be missing!", location='json')
            parser.add_argument('bowling_style', type=str, required=True, help="Bowling style cannot be missing!", location='json')
            parser.add_argument('bowling_cat', type=str, required=True, help="Bowling category cannot be missing!", location='json')
            parser.add_argument('type', type=str, required=True, help="Type cannot be missing!", location='json')
            # parser.add_argument('status', type=str, required=True, help="Status cannot be missing!", location='json')
            parser.add_argument('team', type=str, required=True, help="Team cannot be missing!", location='json')
            args = parser.parse_args()
            query_id= """
                INSERT INTO PLAYER (NAME,FIRST_NAME,LAST_NAME, BATTING_STYLE, BOWLING_STYLE, BOWLING_CAT, TYPE, TEAM_ID) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING ID 
            """
            params = (args['name'],args['first_name'],args['last_name'], args['batting_style'], args['bowling_style'], args['bowling_cat'],args['type'], args['team'])
            player_id = writeFetchSQL(query_id, params)
            if player_id:
                insert_query= """
                    INSERT INTO TEAMPLAYERS (P_ID, T_ID, STATUS) 
                    SELECT %s, %s, %s WHERE NOT EXISTS 
                    ( SELECT id FROM TEAMPLAYERS WHERE P_ID = %s AND T_ID = %s )
                    
                """
                params = (player_id, args['team'], True, player_id, args['team'])
                teamplayers = writeSQL(insert_query, params)
                if teamplayers:
                    return { 'success' : True, 'message': 'Successfully created'}, 200
                else:
                    return {'sucess' : False }, 400        
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500

    def put(self):
        try:
            parser = reqparse.RequestParser(bundle_errors=True)
            parser.add_argument('name', type=str, required=True, help="Name of the Player cannot be missing!", location='json')
            parser.add_argument('first_name', type=str, required=True, help="First Name of the Player cannot be missing!", location='json')
            parser.add_argument('last_name', type=str, required=True, help="Last Name of the Player cannot be missing!", location='json')
            parser.add_argument('batting_style', type=str, required=True, help="Batting style cannot be missing!", location='json')
            parser.add_argument('bowling_style', type=str, required=True, help="Bowling style cannot be missing!", location='json')
            parser.add_argument('bowling_cat', type=str, required=True, help="Bowling category cannot be missing!", location='json')
            parser.add_argument('type', type=str, required=True, help="Type cannot be missing!", location='json')
            # parser.add_argument('status', type=str, required=True, help="Status cannot be missing!", location='json')
            parser.add_argument('team', type=int, required=True, help="Team cannot be missing!", location='json')
            parser.add_argument('id', type=int, required=True, help="Team cannot be missing!", location='json')
            args = parser.parse_args()
            query_insert= """
                UPDATE PLAYER SET NAME = %s, FIRST_NAME= %s, LAST_NAME= %s,  BATTING_STYLE = %s, BOWLING_STYLE = %s,BOWLING_CAT = %s, TYPE = %s, TEAM_ID = %s WHERE ID = %s
            """
            params = (args['name'], args['first_name'], args['last_name'], args['batting_style'], args['bowling_style'],args['bowling_cat'], args['type'], args['team'], args['id'])
            players = writeSQL(query_insert, params)
            if players:
                return { 'success' : True, 'message': 'Updated successfully'}, 200
            else:
                return {'sucess' : False }, 400        
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500
            