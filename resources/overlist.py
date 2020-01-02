from flask_restful import Resource, reqparse, request
from common.db import writeSQL, readSQL, readManySQL
import app, json
from common.util import default


class OverList(Resource):
    @app.jwt_required
    def get(self):
        try:
            args = request.args
            if 'match_id' in args:
                query_match= """
                    SELECT SCORE_ID FROM MATCH WHERE ID = %s
                    """
                params = (args['match_id'],)
                row_score = readSQL(query_match, params)
                if row_score:
                    query_score= """
                    SELECT SCORECARD_ID FROM SCORE WHERE ID = %s
                    """
                    params = (row_score['score_id'],)
                    row_scorecard_id = readSQL(query_score, params)
                    if row_scorecard_id:
                        over = ''
                        query_playercard= """
                                    select id, ball_id, team_a_over, team_b_over, innings from playerscorecard where s_id = %s
                                    order by innings, team_a_over, team_b_over 
                                    """
                        params = (row_scorecard_id['scorecard_id'],)
                        row_match = readManySQL(query_playercard, params)
                        innings_1_list = []
                        innings_2_list = []
                        for over in row_match:
                            if over['innings'] == 1:
                                inning_1 = {}
                                inning_1['id'] = over['id']
                                inning_1['innings'] = over['innings']
                                inning_1['over'] = over['team_a_over']
                                inning_1['ball_id'] = over['ball_id']
                                innings_1_list.append(inning_1)
                        for over in row_match:
                            if over['innings'] == 2:
                                inning_2 = {}
                                inning_2['id'] = over['id']
                                inning_2['innings'] = over['innings']
                                inning_2['over'] = over['team_b_over']
                                inning_2['ball_id'] = over['ball_id']
                                innings_2_list.append(inning_2)
                        get_curr_inng = app.redis.get("match:"+str(args['match_id'])+":innings")
                        curr_livecard = {}
                        if get_curr_inng:
                            get_inng = json.loads(get_curr_inng)
                            curr_key = "livescorecard:"+str(args['match_id'])+":current:"+str(get_inng)
                            curr_livecard = json.loads(app.redis.get(curr_key))
                            curr_livecard['innings'] = get_inng
                        data = json.dumps({'success' : True, 'innings_1': innings_1_list, 'innings_2': innings_2_list, 'status': curr_livecard}, default=default)
                        return json.loads(data), 200
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500