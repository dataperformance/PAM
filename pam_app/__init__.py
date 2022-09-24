"""init the app"""
import yaml
# check service and load env vars
with open("./app.yaml", "r") as stream:
    try:
        app_config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
    except Exception as ex:
        print(ex)
service = app_config['service']
api_version_number = app_config['env_variables']['API_VERSION_NUMBER']  # get the API version number
jwt_access_token_expires_day = app_config['env_variables']['JWT_ACCESS_TOKEN_EXPIRES']

from flask import Flask, jsonify, Blueprint
from pam_app.resources.team import team
from pam_app.resources.study import study
from pam_app.resources.participant import participant
from pam_app.resources.auth import auth
from pam_app.resources.index import index
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

from pam_app.database.db import initialize_db
import datetime
from config_module import Local, QA, Production


def create_app():
    app = Flask(__name__, template_folder="templates")
    # print(app_config)
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=int(jwt_access_token_expires_day))

    # check the service
    if service == "local":  # if run local
        app.config.from_object(Local)
    if service == "pam-qa":
        pam_qa_config = QA()
        app.config.from_object(pam_qa_config)
    if service == "pam":
        pam_config = Production()
        app.config.from_object(pam_config)

    print(f'current version: V{str(api_version_number)}, service: {str(service)} ')

    # assign version number to the api
    version = Blueprint(
        'version{}'.format(api_version_number),
        __name__,
        url_prefix='/api/v{}'.format(api_version_number)
    )
    # register blueprints
    version.register_blueprint(team)
    version.register_blueprint(study)
    version.register_blueprint(participant)
    version.register_blueprint(auth)
    app.register_blueprint(version)
    app.register_blueprint(index)

    # init database
    initialize_db(app)
    # initialize JWTManager
    jwt = JWTManager(app)
    bcrypt = Bcrypt(app)

    @jwt.expired_token_loader
    def my_expired_token_callback(*args, **kwargs):
        return jsonify({
            'msg': 'The user token is invalid'
        }), 401

    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)

    return app
