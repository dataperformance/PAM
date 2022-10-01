from flask import Blueprint, request, jsonify
from pam_app.database.models import User, Team, Study
import uuid
import datetime
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import json
from .exception import AuthError, UserValidationError
from . import request_handler
from . import error_handler

auth = Blueprint('auth', __name__)
# register error handler
auth.register_blueprint(error_handler.error_bp)


@auth.route("/user/register", methods=["POST"])
def register():
    # store the json body request
    register_detail = request_handler(request, "email", "password")

    email, password = register_detail['email'], register_detail['password']

    # check if account exists
    account = User.objects(email=email)

    if not account:
        # create new account
        userId = str(uuid.uuid4())
        user_created = User(email=email, password=password, userId=userId)  # userId is the id in the db
        # hash the password
        user_created.hash_password()
        user_created.save()

        return jsonify({"msg": "create success", 'userId': userId}), 200
    else:
        raise AuthError("User already exists", status_code=409)


@auth.route("/user/login", methods=["POST"])
def login():
    login_details = request_handler(request, "email", "password")
    try:
        user = User.objects.get_or_404(email=login_details['email'])  # search for user in database
    except Exception as e:
        raise AuthError("User not found", status_code=404)
    # check password
    authorized = user.check_password(login_details.get('password'))
    if not authorized:
        raise AuthError("Invalid password", status_code=401)
    # 7 days for the token to expire
    expires = datetime.timedelta(days=7)
    access_token = create_access_token(identity=str(user.userId), expires_delta=expires)  #
    return jsonify({"msg": "login success", 'token': access_token}), 200


# add a user to the team by input email
@auth.route('/team/add/user', methods=['PATCH'])
@jwt_required()
def add_user_team():
    """
    add a user to the team by input email
    input:{
    email
    }
    """
    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    try:
        user = User.objects.get_or_404(userId=userId)  # find the user obj
    except Exception as e:
        raise UserValidationError()

    """request body"""
    # get the user according to the email

    Data = request_handler(request, 'email', 'teamName')
    userEmail = Data['email']
    teamName = Data['teamName']
    memberUser = User.objects(email=userEmail).first()
    team = Team.objects(teamName=teamName).first()
    if memberUser is None:
        # return jsonify({'msg': "Invalid user email"}), 404
        raise UserValidationError('user not found in the database')
    if team is None:
        # return jsonify({'msg': "Invalid teamName"}), 404
        raise AuthError("Team not found", status_code=404)
    if team.owner_user != user:
        raise AuthError("Unauthorized", status_code=403)

    # add the member to the team
    # push the team member only if the team member not in the team
    if memberUser.teams is not None and team in memberUser.teams:
        # return jsonify({'msg': "the member user is already in the team"}), 409
        raise UserValidationError("the member user is already in the team", 409)
    team.update(add_to_set__member_users=memberUser)
    # update the user
    memberUser.update(add_to_set__teams=team)
    return jsonify({'msg': "success"}), 200


# remove a user from a team by input email
@auth.route('/team/remove/user', methods=['PATCH'])
@jwt_required()
def remove_user_team():
    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj

    """request body"""
    try:
        Data = request.get_json()
        userEmail = Data['email']
        teamName = Data['teamName']
        memberUser = User.objects(email=userEmail).first()
        team = Team.objects(teamName=teamName).first()
        if memberUser is None:
            return jsonify({'msg': "Invalid user email"}), 404
        if team is None:
            return jsonify({'msg': "Invalid teamName"}), 404
        if team.owner_user != user:
            return jsonify({'msg': "Unauthorized"}), 401
    except KeyError as KE:
        return jsonify("key Error: {}".format(str(KE))), 404

    if memberUser not in team.member_users:
        return jsonify({'msg': "Team member not found"}), 404

    # pull the user reference from team obj
    team.update(pull__member_users=memberUser)
    # pull the team reference from the user obj
    memberUser.update(pull__teams=team)

    return jsonify({'msg': str(userEmail) + "has been removed from the team"}), 201


# add a user to the minimization study by input email
@auth.route('/study/add/user', methods=['PATCH'])
@jwt_required()
def add_user_study():
    """
    add a user to the minimization study by input member email
    input:{
    user email
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
        studyId = Data['studyId']
        memberUser = User.objects(email=userEmail).first()
        study = Study.objects(studyId=studyId).first()
        if memberUser is None:
            return jsonify({'msg': "Invalid user email"}), 404
        if study is None:
            return jsonify({'msg': "Invalid studyId"}), 404
        if user != study.owner_user:
            return jsonify({'msg': "Unauthorized"}), 401
    except KeyError as KE:
        return jsonify({'msg': "key Error: {}".format(str(KE))}), 404

    # add the member to the minimization study
    # push the user to the study only if the user is in the team
    if memberUser.teams is None or study.owner_team not in memberUser.teams:
        return jsonify({'msg': "the member user is not in the team of the study, please add the member user to the "
                               "team first"}), 409
    elif memberUser in study.member_users:
        return jsonify({'msg': "the member is already in the study"}), 409
    study.update(add_to_set__member_users=memberUser)
    # update the user
    memberUser.update(add_to_set__studies=study)
    return jsonify({'msg': "success"}), 200


# remove a user from a team by input email
@auth.route('/study/remove/user', methods=['PATCH'])
@jwt_required()
def remove_user_study():
    """
    remove a user from the minimization study by input member email
    input:{
    user email
    }
    """
    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj

    """request body"""
    try:
        Data = request.get_json()
        userEmail = Data['email']
        studyId = Data['studyId']
        memberUser = User.objects(email=userEmail).first()
        study = Study.objects(studyId=studyId).first()
        if memberUser is None:
            return jsonify({'msg': "Invalid user email"}), 404
        if study is None:
            return jsonify({'msg': "Invalid teamName"}), 404
        if study.owner_user != user:
            return jsonify({'msg': "Unauthorized"}), 401
    except KeyError as KE:
        return jsonify("key Error: {}".format(str(KE))), 404

    if memberUser not in study.member_users:
        return jsonify({'msg': "Study member not found"}), 404

    # pull the user reference from team obj
    study.update(pull__member_users=memberUser)
    # pull the team reference from the user obj
    memberUser.update(pull__studies=study)
    return jsonify({'msg': str(userEmail) + "has been removed from the team"}), 201
