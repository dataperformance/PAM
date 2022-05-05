from flask import Blueprint, Response, request, jsonify
from database.models import User
import uuid
import datetime
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

auth = Blueprint('auth', __name__)


@auth.route("/api/1.0.0/user/register", methods=["POST"])
def register():
    # store the json body request
    newUser = request.get_json()

    try:
        # hash the password
        password = newUser['password']
        email = newUser['email']
    except Exception as e:
        return jsonify({'msg': 'Invalid input'}), 409

    # check if doc exists
    doc = User.objects(email=email)

    if not doc:
        userId = str(uuid.uuid4())
        user_created = User(email=email, password=password, userId=userId) #userId is the id in the db
        # hash the password
        user_created.hash_password()
        user_created.save()

        return {'userId': userId}, 200
    else:
        return jsonify({'msg': 'Username already exists'}), 409


@auth.route("/api/1.0.0/user/login", methods=["post"])
def login():
    login_details = request.get_json()  # store the json body request
    user = User.objects.get_or_404(email=login_details['email'])  # search for user in database
    # check password
    authorized = user.check_password(login_details.get('password'))
    if not authorized:
        return {'error': 'Email or password invalid'}, 401
    # 7 days for the token to expire
    expires = datetime.timedelta(days=7)
    access_token = create_access_token(identity=str(user.userId), expires_delta=expires) #
    return {'token': access_token}, 200




