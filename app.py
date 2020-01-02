from flask import Flask
from logging.handlers import TimedRotatingFileHandler
import logging
import logging.config
import os
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from flask_cors import CORS
from flask_redis import Redis
from flask_restful import Api

# Resource files
from resources.register import Register
from resources.login import Login
from resources.match import Match
from resources.livescore import LiveScore
from resources.livescorebyball import LiveScoreByBall
from resources.result import Result
from resources.team import Team
from resources.player import Player
from resources.toss import Toss
from resources.matchtype import MatchType
from resources.points import Points
from resources.config import Config
from resources.location import Location
from resources.country import Country
from resources.livescorecard import LiveScoreCard
from resources.fullscorecard import FullScoreCard ,fullscorecard_page
from resources.squad import Squad
from resources.livestatus import LiveStatus
from resources.commentry import Commentry
from resources.manualCommentry import ManualCommentry
from resources.fullcommentry import FullCommentary
from resources.overlist import OverList
from resources.matchlist import MatchList
from resources.undo import Undo
from resources.chart import Chart
from resources.radarChart import RadarChart
from resources.retired import Retired
from resources.penalty import Penalty
from resources.revised import Revised
from resources.pitchChart import PitchChart
from resources.status import Status
from resources.makelive import MakeLive
from resources.substitute import Substitute
from resources.liveCommentry import liveCommentry_page
from resources.quickscorecard import QuickScoreCard
from resources.ucAudioVideo import audio_page,video_page

# Log setting
logname = "logs/lsServer.log"
logging.basicConfig(filename=logname,level=logging.INFO, format='%(process)d %(asctime)s  [%(levelname)s] %(module)s:  %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
log = logging.getLogger(__name__)
handler = TimedRotatingFileHandler(logname, when="midnight", interval=1)
handler.suffix = "%d-%m-%Y"
log.addHandler(handler)

app = Flask(__name__)

#CORS
cors = CORS(app, resources={r"/*": {"origins": "*"}})

# Encryption setting
bcrypt = Bcrypt()
bcrypt.init_app(app)

# Object-based default configuration
config = {
    "production": "config.ProductionConfig",
    "test": "config.TestConfig",
    "default": "config.DevelopmentConfig",
    "local": "config.LocalConfig"
}
config_name = os.getenv('FLASK_CONFIGURATION', 'local')
app.config.from_object(config[config_name])

# JSON web token
jwt = JWTManager(app)

#redis connection
redis = Redis()
redis.init_app(app)

app.register_blueprint(fullscorecard_page)
app.register_blueprint(liveCommentry_page)
app.register_blueprint(audio_page)
app.register_blueprint(video_page)


api = Api(app)
api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(Match, '/match')
api.add_resource(Toss, '/toss')
api.add_resource(LiveScore, '/livescore', '/livescore/<matchid>')
api.add_resource(LiveScoreByBall, '/livescore/<livescorecard_id>/previous')
api.add_resource(Result, '/result')
api.add_resource(Team, '/team')
api.add_resource(Player, '/player')
api.add_resource(MatchType, '/matchtype')
api.add_resource(Points, '/points')
api.add_resource(Config, '/config')
api.add_resource(Location, '/location')
api.add_resource(Country, '/country')
api.add_resource(LiveScoreCard, '/livescorecard')
api.add_resource(FullScoreCard, '/fullscorecard')
api.add_resource(Squad, '/squad')
api.add_resource(LiveStatus, '/livestatus')
api.add_resource(Commentry, '/commentry')
api.add_resource(ManualCommentry,'/manualCommentry', '/manualCommentry/<matchid>')
api.add_resource(FullCommentary, '/fullCommentry')
api.add_resource(OverList, '/overlist')
api.add_resource(MatchList, '/matchlist')
api.add_resource(Undo, '/undo')
api.add_resource(Chart, '/chart')
api.add_resource(RadarChart, '/radarchart')
api.add_resource(Retired, '/retired')
api.add_resource(Penalty, '/penalty')
api.add_resource(Revised, '/revised')
api.add_resource(PitchChart, '/pitchchart')
api.add_resource(Status, '/status')
api.add_resource(MakeLive, '/makelive')
api.add_resource(Substitute, '/substitute')
api.add_resource(QuickScoreCard, '/quickscorecard')

if __name__ == "__main__":
    app.run(host="0.0.0.0")
