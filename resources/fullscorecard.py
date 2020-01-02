from flask_restful import Resource, reqparse, request
from flask import Blueprint, render_template,make_response
from common.db import writeSQL, readSQL, readManySQL
from flask import Markup
import app, json

fullscorecard_page = Blueprint('fullscorecard_page', __name__, template_folder='templates')
@fullscorecard_page.route('/feeds/ucnews/<match_id>/commentry.xml')
def FullScoreCardXML(match_id):
    get_curr_inng = app.redis.get("match:"+str(match_id)+":innings")
    get_inng = json.loads(get_curr_inng)
    offset=0
    limit=20
    list_key = "list:"+str(match_id)+":"+str(get_inng)
    list_commentry = app.redis.lrange(list_key, offset, int(offset)+int(limit) - 1)
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
    commentry_redis_data=pipe.execute()
    commentry_data=[]
    for commentry in commentry_redis_data :
        obj={"comment":''}
        commentry=json.loads(commentry)
        if 'datetime'  in commentry:
            obj["comment"]="<span>"+commentry["datetime"]+"</span>"
        if 'recent'  in commentry:
            score = commentry["recent"].split(' ')
            score = score[len(score) - 1]
            if ( "W" in score and "Wd" not in score) or "+W" in score:
                score = "W"
            if "+NB" in score:
                score = "NB"
            obj["comment"]=obj["comment"]+"<span>"+score+"</span>"
        if 'over'  in commentry:
            obj["comment"]=obj["comment"]+"<span>"+str(commentry["over"])+"</span>"
        obj["comment"]=obj["comment"]+commentry["comment"].replace('id="text"','').replace('<p id="embed">','<span>').replace('<p id="embed">','<span>').replace('</p><p></p>','</span>').replace('id="img"','')
        obj["comment"]=Markup(obj["comment"])
        commentry_data.append(obj)
    query_match= """
                SELECT * FROM MATCH WHERE ID = %s
                """
    params = (match_id,)
    match = readManySQL(query_match, params)
    template = render_template('fullscorecard.xml', match=match[0],commentry_data=commentry_data)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'
    return response

class FullScoreCard(Resource):
    def get(self):
        try:
            args = request.args
            innings = args['innings']
            ball_id = args['ballid']
            match_id = args['matchid']

            # key formation
            key = "fullscorecard:"+str(match_id)+":"+str(innings)+":"+str(ball_id)
            fullcard = app.redis.get(key)
            return { 'success': True, 'data': { 'fullcard': json.loads(fullcard) }}, 200
        except Exception as e:
            print(e)
            app.log.exception(e)
            return {'success': False, 'message': "SERVER/DB error" }, 500
