import app
from flask_restful import Resource, reqparse
from common.db import writeFetchSQL, writeSQL
import app, json

class Result(Resource):
    def put(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('match_id', type=int, required=True, help="Match id cannot be blank!", location='json')
        parser.add_argument('won', type=int, required=True, help="Winning team cannot be blank!", location='json')
        parser.add_argument('team_a', type=int, required=True, help="Team A cannot be blank!", location='json')
        parser.add_argument('team_b', type=int, required=True, help="Team B cannot be blank!", location='json')
        parser.add_argument('team_a_score', type=int, required=True, help="Team A Score cannot be blank!", location='json')
        parser.add_argument('team_b_score', type=int, required=True, help="Team B Score cannot be blank!", location='json')
        parser.add_argument('team_a_name', type=str, required=True, help="Team A name cannot be blank!", location='json')
        parser.add_argument('team_b_name', type=str, required=True, help="Team B name cannot be blank!", location='json')
        parser.add_argument('team_b_wicket', type=int, required=True, help="Team B wicket cannot be blank!", location='json')
        parser.add_argument('nr', type=bool, location='json')
        parser.add_argument('superover', type=bool, location='json')
        args = parser.parse_args()
        try:
            match_id = args['match_id']
            won = args['won']
            nr = args['nr']
            superover = args['superover']
            team_a=args['team_a']
            team_a_score=args['team_a_score']
            team_b=args['team_b']
            team_b_score=args['team_b_score']
            team_b_wicket=args['team_b_wicket']
            team_a_name=args['team_a_name']
            team_b_name=args['team_b_name']
            if(superover or nr):
                if(nr):
                    margin_by_runs = None
                    description = "Match tied"
                    margin_by_wickets = None 
                elif(superover):
                    margin_by_runs = None
                    description = "Match won in super over"
                    margin_by_wickets = None 
            elif(won == team_a):
                margin_by_runs = team_a_score - team_b_score
                description = team_a_name+" won by "+ str(margin_by_runs) + " runs"
                margin_by_wickets = None
            elif(won == team_b):
                margin_by_wickets = 10 - team_b_wicket
                description = team_b_name+" won by "+ str(margin_by_wickets) + " wickets"
                margin_by_runs = None
            query= """
                    INSERT INTO RESULT (WON, NR, SUPEROVER, MARGIN_BY_RUNS, MARGIN_BY_WICKETS, TEAM_A, TEAM_A_SCORE, TEAM_B, TEAM_B_SCORE, TEAM_B_WICKET, DESCRIPTION) 
                    VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING ID;
                    """
            params = (won, nr, superover, margin_by_runs, margin_by_wickets, team_a, team_a_score, team_b, team_b_score, team_b_wicket, description)
            last_id = writeFetchSQL(query, params)
            if last_id:
                query_match= """
                    UPDATE MATCH SET RESULT_ID = %s, STATUS = 'PAST' WHERE ID = %s
                    """
                params = (last_id, match_id)
                count = writeSQL(query_match, params)
                if count:
                    get_curr_inng = app.redis.get("match:"+str(match_id)+":innings")
                    get_inng = json.loads(get_curr_inng)
                    curr_key = "livescorecard:"+str(match_id)+":current:"+str(get_inng)
                    curr_livecard = json.loads(app.redis.get(curr_key))
                    curr_livecard['match_status'] = description
                    app.redis.set(curr_key, json.dumps(curr_livecard))
                    return { 'success' : True }, 200
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500
            