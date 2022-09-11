from flask import Flask, request, Response, jsonify
from database.db import initialize_db
from database.models import Team, Study, Study_SimpleRand, \
    Study_BlockRand, Study_Block, Study_Minimization, Study_Covariables, Study_Participant, Study_RandBlockRand, User
# import blue print
from resources.team import team
from resources.study import study
from resources.participant import participant
from resources.auth import auth
from flask_bcrypt import Bcrypt
# json token
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import datetime

app = Flask(__name__)
app.register_blueprint(team)
app.register_blueprint(study)
app.register_blueprint(participant)
app.register_blueprint(auth)
bcrypt = Bcrypt(app)

# load config from env(deprecated)
# app.config.from_object('config')
from secret_manager import JWT_SECRET_KEY, MONGODB_SETTINGS

app.config["MONGODB_SETTINGS"] = MONGODB_SETTINGS
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY

jwt = JWTManager(app)  # initialize JWTManager


@jwt.expired_token_loader
def my_expired_token_callback(*args, **kwargs):
    return jsonify({
        'msg': 'The user token is invalid'
    }), 401


# JWT toke expiration date
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)

initialize_db(app)

avaliable_allocTypes = {
    "simpleRand": Study_SimpleRand,
    "blockRand": Study_BlockRand,
    "minimization": Study_Minimization,
    'randBlockRand': Study_RandBlockRand
}

if __name__ == '__main__':
    app.run(debug=True)
