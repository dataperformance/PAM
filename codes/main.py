from flask import Flask, jsonify, request
import json
# mongo db
from flask import Flask, request, Response
from Alloc_Algorithm import Trial, Participant

from database.db import initialize_db
from database.models import Team, Study, Study_SimpleRand, \
    Study_BlockRand, Study_Block, Study_Minimization, Study_Covariables, Study_Participant, Study_RandBlockRand, User
import uuid
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
#
bcrypt = Bcrypt(app)

# local test
app.config['MONGODB_SETTINGS'] = {'host': 'mongodb://localhost/db'}

# app.config.from_envvar('ENV_FILE_LOCATION')

# cloud db
# app.config["MONGODB_SETTINGS"] = {'host': "mongodb+srv://davidyin:i9rbUEVAo2rqonq9@cluster0.46hxy.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"}
# secrets.token_hex(20)
app.config["SECRET_KEY"] = '24e7f1128e12e49122c6eed23211ffb51311650f'

jwt = JWTManager(app)  # initialize JWTManager
app.config['JWT_SECRET_KEY'] = '24e7f1128e12e49122c6eed23211ffb51311650f'
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
