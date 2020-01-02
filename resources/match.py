from flask_restful import Resource, reqparse, request
from common.db import writeSQL, readSQL, readManySQL
import app, json
from common.util import default


class Match(Resource):
    @app.jwt_required
    def get(self):
        try:
            args = request.args
            if args:
                if 'status' in args and args['status'] == 'ALL':
                    query_match= """
                        SELECT * FROM MATCH ORDER BY ID ASC
                        """
                    params = (None,)
                elif 'status' in args:
                    query_match= """
                        SELECT * FROM MATCH WHERE STATUS = %s
                        """
                    params = (args['status'],)
                elif 'id' in args:
                    query_match= """
                        SELECT * FROM MATCH WHERE ID = %s
                        """
                    params = (args['id'],)
                row_match = readManySQL(query_match, params)
                if 'status' in args:
                    data = json.dumps({'success' : True, 'data': row_match}, default=default)
                    return json.loads(data), 200
                elif 'id' in args and row_match:
                    query_squad= """
                        SELECT MATCHTYPE.TYPE, MATCHTYPE.NAME AS MATCHTYPE_NAME, FORMAT.NAME AS FORMAT_NAME, FORMAT.OVERS AS FORMAT_OVERS, FORMAT.INNINGS AS FORMAT_INNINGS, TEAMSQUAD.PLAYER_ID AS ID, PLAYER.NAME, PLAYER.FIRST_NAME, PLAYER.LAST_NAME, PLAYER.BOWLING_CAT, PLAYER.BATTING_STYLE, TEAMSQUAD.TEAM_ID AS TEAM, TEAMSQUAD.T_ID_1, TEAMSQUAD.T_ID_2, TEAMSQUAD.SELECTED, TEAMSQUAD.position, TEAMSQUAD.PLAYER_IN FROM MATCH 
                        JOIN SQUAD ON MATCH.SQUAD_ID = SQUAD.ID
                        JOIN TEAMSQUAD ON SQUAD.TEAM_SQUAD_1 = TEAMSQUAD.T_ID_1 OR SQUAD.TEAM_SQUAD_2 = TEAMSQUAD.T_ID_2
                        JOIN PLAYER ON TEAMSQUAD.PLAYER_ID = PLAYER.ID
                        JOIN FORMAT ON FORMAT.ID = MATCH.FORMAT_ID
                        JOIN MATCHTYPE ON MATCHTYPE.ID = MATCH.MATCHTYPE_ID
                        WHERE MATCH.ID = %s
                        ORDER BY TEAMSQUAD.POSITION asc
                        """
                    params = (args['id'],)
                    row_squads = readManySQL(query_squad, params)
                    match_type = row_squads[0]['type']
                    format_name = row_squads[0]['format_name']
                    format_overs = row_squads[0]['format_overs']
                    format_innings = row_squads[0]['format_innings']
                    matchtype_name = row_squads[0]['matchtype_name']
                    match = row_match[0] 
                    team_squad_1 = []
                    team_squad_2 = []
                    for team in row_squads:
                        if team['t_id_1']:
                            team_squad_1.append({
                                    'id': team['id'],
                                    'name': team['name'],
                                    'first_name': team['first_name'],
                                    'last_name': team['last_name'],
                                    'bowling_cat': team['bowling_cat'],
                                    'team': team['team'],
                                    'selected': team['selected'],
                                    'position': team['position'],
                                    'batting_style': team['batting_style'],
                                    'player_in': team['player_in']
                                })
                    for team in row_squads:
                        if team['t_id_2']:
                            team_squad_2.append({
                                    'id': team['id'],
                                    'name': team['name'],
                                    'first_name': team['first_name'],
                                    'last_name': team['last_name'],
                                    'bowling_cat': team['bowling_cat'],
                                    'team': team['team'],
                                    'selected': team['selected'],
                                    'position': team['position'],
                                    'batting_style': team['batting_style'],
                                    'player_in': team['player_in']
                                })
                    query_result= """
                        SELECT * FROM RESULT WHERE ID = %s;
                        """
                    params = (match['result_id'],)
                    row_result = readSQL(query_result, params)
                    obj = {
                        'id': match['id'],
                        'name': match['name'], 
                        'date': match['date'],
                        'local': match['local'],
                        'venue': match['venue'],
                        'toss': match['toss'],
                        'team_a': match['team_a'],
                        'team_b': match['team_b'],
                        'status': match['status'],
                        'team_squad_1': team_squad_1,
                        'team_squad_2' : team_squad_2,
                        'format_id': match['format_id'],
                        'matchtype_id': match['matchtype_id'],
                        'result': row_result,
                        'score_id': match['score_id'],
                        'country_id': match['country_id'],
                        'mom': match['mom'],
                        'match_type': match_type,
                        'format_name': format_name,
                        'format_overs': format_overs,
                        'format_innings': format_innings,
                        'matchtype_name': matchtype_name,
                        'description': match['description']
                    }
                    data = json.dumps({'success' : True, 'data': obj}, default=default)
                    return json.loads(data), 200
                else:
                    return { 'success' : False, 'message': 'match not found' }, 404
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500
    
    @app.jwt_required
    def put(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('id', type=str, required=True, help="match id cannot be missing!", location='json')
        parser.add_argument('name', type=str, required=True, help="Name of the match cannot be missing!", location='json')
        parser.add_argument('date', type=str, required=True, help="Date cannot be missing!", location='json')
        parser.add_argument('venue', type=str, required=True, help="Venue cannot be missing!", location='json')
        parser.add_argument('format', type=int, required=True, help="Format cannot be missing!", location='json')
        parser.add_argument('team_squad_1', type=list,  location='json')
        parser.add_argument('team_squad_2', type=list, location='json')
        parser.add_argument('team_a', type=int, required=True, help="Team A cannot be missing!", location='json')
        parser.add_argument('team_b', type=int, required=True, help="Team B cannot be missing!", location='json')
        parser.add_argument('match_type', type=int, required=True, help="Match Type cannot be missing!", location='json')
        parser.add_argument('country', required=True, type=int, help="Country cannot be missing!", location='json')
        parser.add_argument('match_status', type=str, required=True, location='json')
        parser.add_argument('description', type=str, required=True, help="Description cannot be missing!", location='json')
        args = parser.parse_args()
        try:
            #get format 'id' for the match
            row_format = getMatchFormat(args)
            if row_format is None:
                return { 'success' : False, 'message': 'format not found' }, 404
            
            #get match type 'id' for the match
            row_match_type = getMatchType(args)
            if row_match_type is None:
                return { 'success' : False, 'message': 'match type not found' }, 404


            #get country 'id' for the match
            row_country=getCountry(args)
            if row_country is None:
                return { 'success' : False, 'message': 'country not found' }, 404

            #get team squad ids for the match
            try:
                if args and ('team_squad_1' in args and args['team_squad_1'] ):
                    query_squad= """
                        SELECT * FROM SQUAD WHERE ID = (SELECT SQUAD_ID FROM MATCH WHERE ID = %s)
                        """
                    params = (args['id'],)
                    row_squad = readSQL(query_squad, params)
                    # delete team squad 
                    query_delete_teamsquad= """
                        DELETE FROM TEAMSQUAD WHERE T_ID_1 = %s
                    """
                    params = (row_squad['team_squad_1'],)
                    writeSQL(query_delete_teamsquad, params)
                    # insert team 1 players in team squad
                    for player in args['team_squad_1']:
                        query_team_squad_1= """
                                INSERT INTO TEAMSQUAD (PLAYER_ID, TEAM_ID, T_ID_1, T_ID_2, SELECTED, POSITION, PLAYER_IN) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """
                        params = (player['player'], player['team'], row_squad['team_squad_1'], None, player['status'], player['position'], player['status'])
                        writeSQL(query_team_squad_1, params)
                    
                if args and ('team_squad_2' in args and args['team_squad_2'] ):
                    query_squad_2= """
                        SELECT * FROM SQUAD WHERE ID = (SELECT SQUAD_ID FROM MATCH WHERE ID = %s)
                        """
                    params = (args['id'],)
                    row_squad_2 = readSQL(query_squad_2, params)
                    # delete team squad 
                    query_delete_teamsquad_2= """
                        DELETE FROM TEAMSQUAD WHERE T_ID_2 = %s
                    """
                    params = (row_squad_2['team_squad_2'],)
                    writeSQL(query_delete_teamsquad_2, params)
                    # insert team 2 players in team squad
                    for player in args['team_squad_2']:
                        query_team_squad_2= """
                                INSERT INTO TEAMSQUAD (PLAYER_ID, TEAM_ID, T_ID_1, T_ID_2, SELECTED, POSITION, PLAYER_IN) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """
                        params = (player['player'], player['team'], None, row_squad['team_squad_2'], player['status'], player['position'], player['status'])
                        writeSQL(query_team_squad_2, params)
            except Exception as e:
                app.log.exception(e)
                return {'success': False, 'message': "SERVER/DB error" }, 500

            #match table insertion
            try:
                query= """
                    UPDATE MATCH SET NAME = %s, DATE = %s, VENUE = %s, TEAM_A = %s, TEAM_B = %s, FORMAT_ID = %s, MATCHTYPE_ID = %s, COUNTRY_ID = %s, DESCRIPTION = %s WHERE ID = %s
                    """
                params = (args['name'], args['date'], args['venue'], args['team_a'], args['team_b'], row_format['id'], row_match_type['id'], row_country['id'], args['description'], args['id'])
                count = writeSQL(query, params)
                if count:
                    return { 'success' : True, 'message': 'match is updated' }, 200
            except Exception as e:
                app.log.exception(e)
                return {'success': False, 'message': "SERVER/DB error" }, 500
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500
    
    @app.jwt_required
    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('name', type=str, required=True, help="Name of the match cannot be missing!", location='json')
        parser.add_argument('date', type=str, required=True, help="Date cannot be missing!", location='json')
        parser.add_argument('venue', type=str, required=True, help="Venue cannot be missing!", location='json')
        parser.add_argument('format', type=int, required=True, help="Format cannot be missing!", location='json')
        parser.add_argument('team_squad_1', type=list, required=True, help="Team squad 1 cannot be missing!", location='json')
        parser.add_argument('team_squad_2', type=list, required=True, help="Team squad 2 cannot be missing!", location='json')
        parser.add_argument('team_a', type=int, required=True, help="Team A cannot be missing!", location='json')
        parser.add_argument('team_b', type=int, required=True, help="Team B cannot be missing!", location='json')
        parser.add_argument('match_type', type=int, required=True, help="Match Type cannot be missing!", location='json')
        parser.add_argument('result', type=int, location='json')
        parser.add_argument('country', required=True, type=int, help="Country cannot be missing!", location='json')
        parser.add_argument('mom', type=int, location='json')
        parser.add_argument('match_status', type=str, required=True, location='json')
        parser.add_argument('description', type=str, required=True, help="Description cannot be missing!", location='json')
        args = parser.parse_args()
        
        try:
            #get format 'id' for the match
            row_format = getMatchFormat(args)
            if row_format is None:
                return { 'success' : False, 'message': 'format not found' }, 404
            
            #get match type 'id' for the match
            row_match_type = getMatchType(args)
            if row_match_type is None:
                return { 'success' : False, 'message': 'match type not found' }, 404


            #get country 'id' for the match
            row_country=getCountry(args)
            if row_country is None:
                return { 'success' : False, 'message': 'country not found' }, 404

            #get team squad ids for the match
            try:
                if args and ('team_squad_1' in args and 'team_squad_2' in args):
                    query_squad= """
                    SELECT TEAM_SQUAD_1, TEAM_SQUAD_2 FROM squad ORDER BY ID desc limit 1
                    """
                    row_squad = readSQL(query_squad, None)
                    if row_squad is None:
                        t_id_1 = 1
                        t_id_2 = 2
                    else:
                        t_id_1 = row_squad['team_squad_1'] + 2
                        t_id_2 = row_squad['team_squad_2'] + 2
                    insert_squad= """
                        INSERT INTO SQUAD (TEAM_SQUAD_1, TEAM_SQUAD_2) 
                        VALUES (%s, %s)
                    """
                    params = (t_id_1, t_id_2)
                    writeSQL(insert_squad, params)
                    # insert team 1 players in team squad
                    for player in args['team_squad_1']:
                        query_team_squad_1= """
                                INSERT INTO TEAMSQUAD (PLAYER_ID, TEAM_ID, T_ID_1, T_ID_2, SELECTED, POSITION, PLAYER_IN) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """
                        params = (player['player'], player['team'], t_id_1, None, player['status'], player['position'], player['status'])
                        writeSQL(query_team_squad_1, params)
                    
                    # insert team 2 players in team squad
                    for player in args['team_squad_2']:
                        query_team_squad_2= """
                                INSERT INTO TEAMSQUAD (PLAYER_ID, TEAM_ID, T_ID_1, T_ID_2, SELECTED, POSITION, PLAYER_IN) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """
                        params = (player['player'], player['team'], None, t_id_2, player['status'], player['position'], player['status'])
                        writeSQL(query_team_squad_2, params)
            except Exception as e:
                query_delete_teamsquad= """
                        DELETE FROM TEAMSQUAD WHERE T_ID_1 = %s OR T_ID_2 = %s
                    """
                params = (t_id_1, t_id_2)
                writeSQL(query_delete_teamsquad, params)
                if t_id_1 and t_id_2:
                    query_delete_squad= """
                            DELETE FROM SQUAD WHERE TEAM_SQUAD_1 = %s OR TEAM_SQUAD_2 = %s
                        """
                    params = (t_id_1, t_id_2)
                    writeSQL(query_delete_squad, params)
                app.log.exception(e)
                return {'success': False, 'message': "SERVER/DB error" }, 500

            #get score squad ids for the match  
            try:
                query_score= """
                SELECT SCORECARD_ID FROM SCORE ORDER BY ID desc limit 1
                """
                row_score = readSQL(query_score, None)
                if row_score is None:
                    s_id = 1
                else:
                    s_id = row_score['scorecard_id'] + 1
                query= """
                    INSERT INTO SCORE (SCORECARD_ID) 
                    VALUES (%s)"""
                params = (s_id,)
                writeSQL(query, params)
            except Exception as e:
                query_delete_teamsquad= """
                        DELETE FROM TEAMSQUAD WHERE T_ID_1 = %s OR T_ID_2 = %s
                    """
                params = (t_id_1, t_id_2)
                writeSQL(query_delete_teamsquad, params)
                if t_id_1 and t_id_2:
                    query_delete_squad= """
                            DELETE FROM SQUAD WHERE TEAM_SQUAD_1 = %s OR TEAM_SQUAD_2 = %s
                        """
                    params = (t_id_1, t_id_2)
                    writeSQL(query_delete_squad, params)
                if s_id:
                    query_delete_score= """
                            DELETE FROM SCORE WHERE SCORECARD_ID = %s
                        """
                    params = (s_id,)
                    writeSQL(query_delete_score, params)
                app.log.exception(e)
                return {'success': False, 'message': "SERVER/DB error" }, 500

            #match table insertion
            try:
                query_squad= """
                SELECT ID FROM SQUAD ORDER BY ID desc limit 1
                """ 
                row_squad = readSQL(query_squad, None)
                query_score= """
                SELECT ID FROM SCORE ORDER BY ID desc limit 1
                """ 
                row_score = readSQL(query_score, None)
                query= """
                    INSERT INTO MATCH (NAME, DATE, VENUE, TEAM_A, TEAM_B, STATUS, SQUAD_ID, FORMAT_ID, MATCHTYPE_ID, SCORE_ID, COUNTRY_ID, DESCRIPTION ) 
                    VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                params = (args['name'], args['date'], args['venue'], args['team_a'], args['team_b'], args['match_status'], row_squad['id'], row_format['id'], row_match_type['id'], row_score['id'], row_country['id'], args['description'])
                count = writeSQL(query, params)
                if count:
                    return { 'success' : True, 'message': 'match is created' }, 200
            except Exception as e:
                query_delete_teamsquad= """
                        DELETE FROM TEAMSQUAD WHERE T_ID_1 = %s OR T_ID_2 = %s
                    """
                params = (t_id_1, t_id_2)
                writeSQL(query_delete_teamsquad, params)
                if t_id_1 and t_id_2:
                    query_delete_squad= """
                            DELETE FROM SQUAD WHERE TEAM_SQUAD_1 = %s OR TEAM_SQUAD_2 = %s
                        """
                    params = (t_id_1, t_id_2)
                    writeSQL(query_delete_squad, params)
                if s_id:
                    query_delete_score= """
                            DELETE FROM SCORE WHERE SCORECARD_ID = %s
                        """
                    params = (s_id,)
                    writeSQL(query_delete_score, params)
                app.log.exception(e)
                return {'success': False, 'message': "SERVER/DB error" }, 500
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500

def getCountry(args):
    try:
        if args and 'country' in args:
            query_country= """
                SELECT ID FROM COUNTRY WHERE ID = %s
                """
            params = (args['country'],)
            row_country = readSQL(query_country, params)
            return row_country
    except Exception as e:
        app.log.exception(e)
        raise e

def getMatchFormat(args):
    try:
        if args and 'format' in args:
            query_format= """
                SELECT ID FROM FORMAT WHERE ID = %s
                """
            params = (args['format'],)
            row_format = readSQL(query_format, params)
            return row_format
    except Exception as e:
        app.log.exception(e)
        raise e

def getMatchType(args):
    try:
        if args and 'match_type' in args:
            query_matchtype= """
                SELECT ID FROM MATCHTYPE WHERE ID = %s
                """
            params = (args['match_type'],)
            row_match_type = readSQL(query_matchtype, params)
            return row_match_type
    except Exception as e:
        app.log.exception(e)
        raise e
