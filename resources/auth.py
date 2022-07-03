from flask import Blueprint, Response, request, jsonify
from database.models import User, Team
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
        user_created = User(email=email, password=password, userId=userId)  # userId is the id in the db
        # hash the password
        user_created.hash_password()
        user_created.save()

        return {'userId': userId}, 200
    else:
        return jsonify({'msg': 'Username already exists'}), 409


@auth.route("/api/1.0.0/user/login", methods=["POST"])
def login():
    login_details = request.get_json()  # store the json body request
    user = User.objects.get_or_404(email=login_details['email'])  # search for user in database
    # check password
    authorized = user.check_password(login_details.get('password'))
    if not authorized:
        return {'error': 'Email or password invalid'}, 401
    # 7 days for the token to expire
    expires = datetime.timedelta(days=7)
    access_token = create_access_token(identity=str(user.userId), expires_delta=expires)  #
    return {'token': access_token}, 200


# add a user to the team by input email
@auth.route('/api/1.0.0/team/add/user', methods=['PATCH'])
@jwt_required()
def add_user():
    """
    add a user to the team by input email
    input:{
    email
    }
    """
    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj

    """request body"""
    # get the user according to the email
    try:
        Data = request.get_json()
        userEmail = Data['email']
        teamId = Data['teamId']
        memberUser = User.objects(email=userEmail).first()
        team = Team.objects(teamId=teamId).first()
        if memberUser is None:
            return jsonify({'msg':"Invalid user email"}), 404
        if team is None:
            return jsonify({'msg':"Invalid teamId"}), 404
        if team.owner_user != user:
            return jsonify({'msg':"Unauthorized"}), 401
    except KeyError as KE:
        return jsonify({'msg':"key Error: {}".format(str(KE))}), 404

    # add the member to the team
    # push the team member only if the team member not in the team
    if memberUser.teams is not None and team in memberUser.teams:
        return jsonify({'msg':"the member user is already in the team"}), 409
    team.update(add_to_set__member_users=memberUser)
    # update the user
    memberUser.update(add_to_set__teams=team)
    return jsonify({'msg':"success"}), 200


# remove a user from a team by input email
@auth.route('/api/1.0.0/team/remove/user', methods=['PATCH'])
@jwt_required()
def remove_user():
    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj

    """request body"""
    try:
        Data = request.get_json()
        userEmail = Data['email']
        teamId = Data['teamId']
        memberUser = User.objects(email=userEmail).first()
        team = Team.objects(teamId=teamId).first()
        if memberUser is None:
            return jsonify({'msg':"Invalid user email"}), 404
        if team is None:
            return jsonify({'msg':"Invalid teamId"}), 404
        if team.owner_user != user:
            return jsonify({'msg':"Unauthorized"}), 401
    except KeyError as KE:
        return jsonify("key Error: {}".format(str(KE))), 404

    if memberUser not in team.member_users:
        return jsonify({'msg':"Team member not found"}), 404

    # pull the user reference from team obj
    team.update(pull__member_users=memberUser)
    # pull the team reference from the user obj
    memberUser.update(pull__teams=team)

    return jsonify({'msg': str(userEmail)+"has been removed from the team"}), 201
