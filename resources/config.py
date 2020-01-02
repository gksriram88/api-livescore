from flask_restful import Resource, reqparse, request
from common.db import writeSQL, readSQL, readManySQL
import app, json
from common.util import default


class Config(Resource):
    def get(self):
        try:
            all_data = {}

            # team list
            query_teams = """
                SELECT ID, NAME, STATUS, SHORTNAME FROM TEAM
            """
            teams = readManySQL(query_teams, None)
            # all_data.append({'teams' : teams})
            team_enum = {}
            for item in teams:
                team_enum[item['id']] = item['name']
            
            team_enum_short = {}
            for item in teams:
                team_enum_short[item['id']] = item['shortname']
            # all_data.append({'team_enum': team_enum})

            # country list
            query_country = """
                SELECT ID, NAME, STATUS FROM COUNTRY
            """
            countries = readManySQL(query_country, None)
            country_enum = {}
            for item in countries:
                country_enum[item['id']] = item['name']

            # match type list
            query_match_type = """
                SELECT ID, TYPE, NAME, VENUE FROM MATCHTYPE
            """
            match_type = readManySQL(query_match_type, None)
            match_type_enum = {}
            series_match_list=[]
            tournament_match_list=[]
            series_match={}
            tournament_match={}
            for item in match_type:
                match_type_enum[item['id']] = item['name']
                if item['type']=="SERIES":
                    series_match={
                        "id":item['id'],
                        "name":item['name']
                        }
                    series_match_list.append(series_match)
                    series_match={}
                elif item['type']=="TOURNAMENT":
                    tournament_match={
                        "id":item['id'],
                        "name":item['name']
                        }
                    tournament_match_list.append(tournament_match)
                    tournament_match={}
            
            #ball type  list
            query_balltype = """
                SELECT ID, NAME, DISPLAY_NAME, STATUS FROM BALLTYPE
            """
            ball_types = readManySQL(query_balltype, None)
            balltype_enum = {}
            for item in ball_types:
                balltype_enum[item['id']] = item['display_name']

            #ball type cat list
            query_cattype = """
                SELECT BALL_CAT FROM BALLTYPE GROUP BY BALL_CAT
            """
            ball_type = readManySQL(query_cattype, None)
            balltype_spin = []
            balltype_fast = []
            balltype_common = []
            for item in ball_type:
                if(item['ball_cat'] == 'spin'):
                    query_balltype = """
                    SELECT * FROM BALLTYPE WHERE BALL_CAT = %s
                    """
                    params = (item['ball_cat'],)
                    ball_type = readManySQL(query_balltype, params)
                    balltype_spin = ball_type
                elif(item['ball_cat'] == 'fast'):
                    query_balltype = """
                    SELECT * FROM BALLTYPE WHERE BALL_CAT = %s
                    """
                    params = (item['ball_cat'],)
                    ball_type = readManySQL(query_balltype, params)
                    balltype_fast = ball_type
                elif(item['ball_cat'] == 'common'):
                    query_balltype = """
                    SELECT * FROM BALLTYPE WHERE BALL_CAT = %s
                    """
                    params = (item['ball_cat'],)
                    ball_type = readManySQL(query_balltype, params)
                    balltype_common = ball_type
                

            #short type list
            query_shottype = """
                SELECT ID, NAME, STATUS, DISPLAY_NAME FROM SHOTTYPE
            """
            shot_type = readManySQL(query_shottype, None)
            shotype_enum = {}
            for item in shot_type:
                shotype_enum[item['id']] = item['display_name']

            #out type list
            query_outtype = """
                SELECT ID, NAME, STATUS FROM OUT
            """
            out_type = readManySQL(query_outtype, None)

            #format type list
            query_format = """
                SELECT ID, NAME, STATUS, OVERS, INNINGS FROM FORMAT
            """
            format_type = readManySQL(query_format, None)
            format_type_enum = {}
            for item in format_type:
                format_type_enum[item['id']] = item['name']
            
            #match status
            query_statustype = """
                SELECT ID, NAME, LOCK FROM STATUS
            """
            status_type = readManySQL(query_statustype, None)
            statustype_enum = {}
            for item in status_type:
                statustype_enum[item['id']] = item['name']

            #field position
            query_fieldpos = """
                SELECT ID, NAME, STATUS FROM FIELDPOSITION
            """
            field_pos = readManySQL(query_fieldpos, None)
            fieldpos_enum = {}
            for item in field_pos:
                fieldpos_enum[item['id']] = item['name']

            all_data={'teams' : teams, 
            'team_enum': team_enum, 
            'team_enum_short': team_enum_short,
            'countries':countries,
            'country_enum':country_enum,
            'balltype': ball_types, 
            'balltype_enum': balltype_enum,
            'balltype_spin': balltype_spin,
            'balltype_fast': balltype_fast,
            'balltype_common': balltype_common,
            'shot_type': shot_type,
            'shottype_enum': shotype_enum, 
            'out_type': out_type, 
            'format_type': format_type,
            'format_type_enum':format_type_enum,
            'match_type':match_type,
            'match_type_enum':match_type_enum,
            'series_match_list':series_match_list,
            'tournament_match_list':tournament_match_list,
            'match_status': status_type,
            'match_status_enum': statustype_enum,
            'field_position_enum': fieldpos_enum,
            'field_position': field_pos}
            return {'success': True, 'data': all_data}, 200
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500