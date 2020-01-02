# from flask import Flask
# from logging.handlers import TimedRotatingFileHandler
# import logging
# import logging.config
# import os
# from flask_bcrypt import Bcrypt
# from flask_jwt_extended import (
#     JWTManager, jwt_required, create_access_token,
#     get_jwt_identity
# )

# # Log setting
# logname = "logs/lsServer.log"
# logging.basicConfig(filename=logname,level=logging.INFO, format='%(process)d %(asctime)s  [%(levelname)s] %(module)s:  %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
# log = logging.getLogger(__name__)
# handler = TimedRotatingFileHandler(logname, when="M", interval=1)
# handler.suffix = "%d-%m-%Y"
# log.addHandler(handler)

# app = Flask(__name__)

# # Encryption setting
# bcrypt = Bcrypt(app)

# # Object-based default configuration
# config = {
#     "production": "livescore.config.ProductionConfig",
#     "test": "livescore.config.TestConfig",
#     "default": "livescore.config.DevelopmentConfig",
#     "local": "livescore.config.LocalConfig"
# }
# config_name = os.getenv('FLASK_CONFIGURATION', 'default')
# app.config.from_object(config[config_name])

# # JSON web token
# jwt = JWTManager(app)

# import livescore.app

# #if __name__ == "__main__":
# #    app.run()