from flask_restful import Resource, reqparse, request
from common.db import writeSQL, readSQL, readManySQL
import app, json
from common.util import default


class Toss(Resource):
    @app.jwt_required
    def put(self):
        try:
            parser = reqparse.RequestParser(bundle_errors=True)
            parser.add_argument('id', type=str, required=True, help="match id cannot be missing!", location='json')
            parser.add_argument('team_a', type=int, required=True, help="team id a cannot be missing!", location='json')
            parser.add_argument('team_b', type=int, required=True, help="team id b cannot be missing!", location='json')
            parser.add_argument('toss', type=int, required=True, help="toss cannot be missing!", location='json')
            args = parser.parse_args()
            update_match= """
                UPDATE MATCH SET TEAM_A = %s, TEAM_B = %s, TOSS = %s WHERE ID = %s
            """
            params = (args['team_a'], args['team_b'], args['toss'], args['id'])
            update = writeSQL(update_match, params)
            if update:
                query_match_toss= """
                        select match.team_a, match.team_b, match.toss, teama.name as team_a_name, teamb.name as team_b_name  from "match"
                        join team as teama on match.team_a = teama.id 
                        join team as teamb on match.team_b = teamb.id
                        where match.id = %s
                        """
                params = (args['id'],)
                row_match = readSQL(query_match_toss, params)
                if row_match:
                    teamA_name = row_match['team_a_name']
                    teamB_name = row_match['team_b_name']
                    match_status = ''
                    if row_match['toss'] == args['team_a']:
                        if row_match['team_a'] == args['team_a']:
                            match_status = row_match['team_a_name']+" won the toss and elected to bat first"
                        else:
                            match_status = row_match['team_a_name']+" won the toss and elected to field first"
                    elif row_match['toss'] == args['team_b']:
                        if row_match['team_b'] == args['team_a']:
                            match_status = row_match['team_b_name']+" won the toss and elected to bat first"
                        else:
                            match_status = row_match['team_b_name']+" won the toss and elected to field first"
                    inn_key = "match:"+str(args['id'])+":innings"
                    live_key_1 = "livescorecard:"+str(args['id'])+":current:1"
                    live_val_1 = json.dumps({'over': "0.0", 'ball': 0, 'match_status': match_status})
                    live_key_2 = "livescorecard:"+str(args['id'])+":current:2"
                    live_val_2 = json.dumps({'over': "0.0", 'ball': 0, 'match_status': 'Innings 2 is in progress'})
                    quick_key_1 = "quickscorecard:"+str(args['id'])+":current:1"
                    quick_val_1 = json.dumps({'score': "0/0 (0.0)", 'team': teamA_name})
                    quick_key_2 = "quickscorecard:"+str(args['id'])+":current:2"
                    quick_val_2 = json.dumps({'score': "0/0 (0.0)", 'team': teamB_name})
                    app.redis.set(inn_key, 1)
                    app.redis.set(live_key_1, live_val_1)
                    app.redis.set(live_key_2, live_val_2)
                    app.redis.set(quick_key_1, quick_val_1)
                    app.redis.set(quick_key_2, quick_val_2)
                    return {'success': True }, 200
            else:
                return {'success': False, 'message': 'no match found' }, 404
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500
    