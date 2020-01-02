from flask_restful import Resource, reqparse, request
from flask import Blueprint, render_template,make_response
from common.db import writeSQL, readSQL, readManySQL
from datetime import date
import time
import datetime
import app, json

liveCommentry_page = Blueprint('liveCommentry_page', __name__, template_folder='templates')
@liveCommentry_page.route('/LiveCommentary.xml')
def LiveCommentaryXML():
    team={
        "Australia":1,
        "England":2,
        "India":3,
        "New Zealand":4,
        "Pakistan":5,
        "South Africa":6,
        "Sri Lanka":7,
        "West Indies":8,
        "Zimbabwe":9,
        "Bangladesh":10,
        "Netherlands":14,
        "Scotland":15,
        "Ireland":24,
        "Oman":93,
        "Afganistan":95,
        "Papua New Guinea":267
    }
    today = date.today()
    today = today.strftime("%Y-%m-%d")
    query_match= """
                select match.id, match.name, date,teama.id as teamaID, teama.name as teama, teamb.id as teambID,teamb.name as teamb, teamb.logo as teamb_logo,match.date, match.venue  from "match"
                join team as teama on teama.id = match.team_a 
                join team as teamb on teamb.id = match.team_b
                join matchtype on matchtype.id = match.matchtype_id
                where match.status = %s
                """
    params = ("UPCOMING",)
    matchs = readManySQL(query_match, params)
    obj={}
    matchData=[]
    for match in matchs:
        obj=match
        obj["teamaid"]=team[match["teama"]]
        obj["teambid"]=team[match["teamb"]]
        date_time_obj = match["date"]  
        obj["game_date"]=date_time_obj.date().strftime("%Y%m%d")
        obj["game_date_string"]=date_time_obj.date().strftime('%dth %b %Y')
        obj["game_date_time"]=date_time_obj
        obj["time"]=date_time_obj.time()
        matchData.append(obj)
    template = render_template('LiveCommentary.xml',today=today,matchData=matchData)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'
    return response