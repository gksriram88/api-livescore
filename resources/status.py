from flask_restful import Resource, reqparse, request
from common.db import writeSQL, readSQL, readManySQL
import app, json, math
from common.util import default
from datetime import datetime


class Status(Resource):
    def get(self):
        try:
            args = request.args
            if 'id' in args:
                query_status= """
                    SELECT * FROM STATUS WHERE ID = %s 
                    """
                params = (args['id'],)
                row_status = readSQL(query_status, params)
                if row_status:
                    return { 'success': True, 'data': row_status }, 200
                else:
                    return { 'success': False, 'message': 'no data found' }, 404
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500

    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('name', type=str, required=True, help="Name of the status cannot be missing!", location='json')
        parser.add_argument('lock', type=bool, required=True, help="lock cannot be missing!", location='json')
        parser.add_argument('match_id', type=int, required=True, help="Match ID cannot be missing!", location='json')
        args = parser.parse_args()
        try:
            insert_status= """
                INSERT INTO STATUS (NAME, LOCK) 
                VALUES (%s, %s)
                """
            params = (args['name'], args['lock'])
            row_status = writeSQL(insert_status, params)
            if row_status:
                get_curr_inng = app.redis.get("match:"+str(args['match_id'])+":innings")
                if get_curr_inng:
                    get_inng = json.loads(get_curr_inng)
                    curr_key = "livescorecard:"+str(args['match_id'])+":current:"+str(get_inng)
                    curr_livecard = json.loads(app.redis.get(curr_key))
                    curr_livecard['match_status'] = args['name']
                    update_status = app.redis.set(curr_key, json.dumps(curr_livecard))
                    if update_status:
                        #manual commentry
                        list_com = "list:"+str(args['match_id'])+":"+str(get_inng)
                        man_com_key = "commentry:"+str(args['match_id'])+":"+str(get_inng)+":manual"
                        obj = {}
                        obj['comment'] = args['name']
                        obj['datetime'] = datetime.utcnow()
                        if(app.redis.hkeys(man_com_key)):
                            index_val = [val for loc, val in enumerate(app.redis.hkeys(man_com_key)) if math.floor(float(val)) == curr_livecard['ball']]
                            if(index_val):
                                max_val = float(max(index_val))
                                field_key = format(max_val + 0.1, ".1f")
                            else:
                                field_key = curr_livecard['ball'] + 0.1
                        else:
                            field_key = curr_livecard['ball'] + 0.1
                        list_man_com_key = man_com_key+":"+str(field_key)
                        app.redis.lpush(list_com, list_man_com_key)
                        app.redis.hset(man_com_key, field_key, json.dumps(obj, default=default))
                        return { 'success': True }, 200
                else:
                    return { 'success': False, 'message': 'no match id found' }, 404
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500
    
    def put(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('id', type=str, required=True, help="Id of the status cannot be missing!", location='json')
        parser.add_argument('name', type=str, required=True, help="Name of the status cannot be missing!", location='json')
        parser.add_argument('lock', type=bool, required=True, help="Lock cannot be missing!", location='json')
        args = parser.parse_args()
        try:
            update_status= """
                UPDATE STATUS SET NAME = %s, LOCK = %s WHERE ID = %s
                """
            params = (args['name'], args['lock'], args['id'])
            row_status = writeSQL(update_status, params)
            if row_status:
                return { 'success': True }, 200
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500

    def delete(self):
        try:
            args = request.args
            if 'id' in args:
                delete_status= """
                    DELETE FROM STATUS WHERE ID = %s
                    """
                params = (args['id'],)
                row_status = writeSQL(delete_status, params)
                if row_status:
                    return { 'success': True }, 200
                else:
                    return { 'success': False, 'message': 'no data found' }, 404
            else:
                return { 'success': False, 'message': 'missing required parameter' }, 400
        except Exception as e:
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500