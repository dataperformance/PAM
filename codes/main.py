from flask import Flask, jsonify, request
import json
from flask import make_response
import sys
#import algorithms
from Alloc_Algorithm._blockRand import block_randomization
from Alloc_Algorithm._simpleRand import simple_rand
from Alloc_Algorithm._blockRand import randomized_block_randomization
#mongo db
from flask import Flask, request, Response
from Alloc_Algorithm import Trial, Participant

from database.db import initialize_db
from database.models import Team,Study, Study_SimpleRand,\
    Study_BlockRand,Study_Block,Study_Minimization,Study_Covariables,Study_Participant,Study_RandBlockRand

import uuid
#import blue print
from resources.team import team
from resources.study import study
from resources.participant import participant


#sys.path.append(r'/Users/David/Desktop/Research/git/SAM/codes/Alloc_Algorithm')

app = Flask(__name__)
app.register_blueprint(team)
app.register_blueprint(study)
app.register_blueprint(participant)

#app.config['MONGODB_SETTINGS'] = {'host': 'mongodb://localhost/test_db'}


app.config["MONGODB_SETTINGS"] = {'host': "mongodb+srv://davidyin:i9rbUEVAo2rqonq9@cluster0.46hxy.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"}
#secrets.token_hex(20)
app.config["SECRET_KEY"] = '24e7f1128e12e49122c6eed23211ffb51311650f'

initialize_db(app)

avaliable_allocTypes = {
    "simpleRand": Study_SimpleRand,
    "blockRand": Study_BlockRand,
    "minimization": Study_Minimization,
    'randBlockRand': Study_RandBlockRand
}








if __name__ == '__main__':
    app.run(debug=True)
