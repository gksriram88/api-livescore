import app, json
from flask_restful import Resource, reqparse, request
from common.db import writeSQL, readSQL, readManySQL
from common.util import default

class FullCommentary(Resource):
    def get(self):
        try:
            args = request.args
            if 'type' in args and args['type'] == 'auto' and 'offset' in args and 'limit' in args and 'id' in args:
                list_key = "list:"+str(args['id'])+":"+str(args['innings'])
                list_commentry = app.redis.lrange(list_key, args['offset'], int(args['offset'])+int(args['limit']) - 1)
                pipe = app.redis.pipeline()
                for key in list_commentry:
                    key_split = key.split(':')
                    if(key_split[3] == 'manual'):
                        key_name = key_split[0]+":"+key_split[1]+":"+key_split[2]+":"+key_split[3]
                        pipe.hget(key_name, key_split[4])
                    else:
                        key_name = key_split[0]+":"+key_split[1]+":"+key_split[2]
                        field_key = key_split[3]
                        pipe.hget(key_name, field_key)
                    
                responses = [json.loads(commentry_data) for commentry_data in pipe.execute()]
                tot_commentry = app.redis.llen(list_key)
                offset = int(args['limit']) + int(args['offset'])
                total = tot_commentry - offset
                if total > 0:
                    return {'success': True, 'data': responses, 'offset': offset}
                else:
                    return {'success': True, 'data': responses}
            elif 'type' in args and args['type'] == 'manual':
                query_comm= """
                SELECT ID, COMMENT, OVER, INNINGS FROM COMM WHERE MATCH_ID = %s AND INNINGS = %s ORDER BY ID DESC LIMIT 6
                """
                params = (args['id'], args['innings'])
                row_comm = readManySQL(query_comm, params)
                if row_comm:
                    data = json.dumps({'success' : True, 'data': row_comm}, default=default)
                    return json.loads(data), 200
            elif 'type' in args and args['type'] == 'updated':
                query_comm= """
                select playerscorecard.team_a_over, playerscorecard.team_b_over, comm."comment" as manual, playerscorecard."comment" as auto from "match"
                join score on "match".score_id = score.id
                join playerscorecard on playerscorecard.s_id = score.scorecard_id
                join comm on match.id = comm.match_id and playerscorecard.innings = comm.innings and comm.over = playerscorecard.team_a_over
                where match.id = %s and comm.innings = %s
                order by comm.id desc limit 6
                """
                params = (args['id'], args['innings'])
                row_comm = readManySQL(query_comm, params)
                if row_comm:
                    row_all = {}
                    row_data_all = []
                    temp = []
                    for data in row_comm:
                        row_all = {}
                        if int(args['innings']) == 1:
                            over = 'team_a_over'
                        else:
                            over = 'team_b_over'
                        row_all['over'] = ''
                        row_all['comment'] = ''
                        if data[over] in temp:
                            for val in row_data_all:
                                if val['over'] == data[over]:
                                    val['comment'] = val['comment'] +' | '+data['manual']
                        else:
                            row_all['over'] = data[over]
                            row_all['comment'] = data['auto'] +' | '+data['manual']
                            row_data_all.append(row_all)
                        temp.append(data[over])
                    data = json.dumps({'success' : True, 'data': row_data_all}, default=default)
                    return json.loads(data), 200
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500


