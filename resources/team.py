import json
import mongoengine.errors
from flask import Blueprint, Response, request, jsonify
from database.models import Team, User
import uuid
from flask_jwt_extended import jwt_required, get_jwt_identity

team = Blueprint('team', __name__)


# get a team or teams
@team.route('/team/', defaults={'teamName': None}, methods=['GET'])  # default teamName is none
@team.route('/team/<teamName>', methods=['GET'])
@jwt_required()
def get_team(teamName):
    """
    get all teams or a team by id
    input:{
    "teamName"
    }
    :return:  {
        "teamName"
        "teamName"
        "studies"
    }
    """
    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj
    teams = user.teams

    """request part"""
    if teamName:
        if not teams: # no team for the user
            return jsonify({'msg': 'the user has no team'})
        try:
            team = Team.objects(teamName=teamName).get_or_404()  # get a team that add by the user

            if team not in teams:
                return jsonify({'msg': "Unauthorized"}), 401
            return Response(team.to_json(), mimetype="application/json", status=200)
        except Exception as e:
            return jsonify(str(e)), 404

    allteams = [] if not teams else [json.loads(team.to_json()) for team in teams]
    view = {'allteams': allteams}
    return jsonify(view), 200


# create a team
@team.route('/team', methods=['POST'])
@jwt_required()  # required auth
def create_team():
    """
    input: {
        "teamName":
    }

    :return: {
    "teamName":UUID,
    "teamName:string"
    }
    """

    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj

    """request part"""
    # read request
    teamData = request.get_json()
    # team id generate
    teamId = uuid.uuid4()

    # add to DB
    try:
        team_created = Team(teamName=teamData['teamName'],
                            owner_user=user,
                            member_users=[user]).save()

    except mongoengine.ValidationError as VE:
        return jsonify({"msg": """teamName should not include special symbols: !@# 
    $%^&*()-+?=,<>/"""})

    except mongoengine.errors.NotUniqueError as e:
        return jsonify({'msg': "teamName need to be unique"}), 400
    # add team to the user

    User.objects(userId=userId).update_one(push__teams=team_created)

    teamName = team_created.teamName

    return {'teamName': teamName}, 200


# update a team by teamName
@team.route('/team/<teamName>', methods=['PATCH'])
@jwt_required()
def update_team(teamName):
    """
    :input teamName:
    :return: update teamName
    """
    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj
    """request part"""

    try:
        new_teamName = request.get_json()['teamName']
        team = Team.objects.get_or_404(teamName=teamName)
        if team.owner_user != user:  # only the owner can modify the team name
            return jsonify({'msg': "Unauthorized"}), 401
        team.update(teamName=new_teamName)
    except mongoengine.errors.NotUniqueError:
        return jsonify({'msg': "teamName need to be unique"}), 409
    except Exception as e:
        return jsonify({'msg': "Invalid request"}), 404

    return jsonify({'msg': "update success"}), 201


# delete a team
@team.route('/team/<teamName>', methods=['DELETE'])
@jwt_required()
def delete_team(teamName):
    """
    delete a team and its all studies
    :input teamName: the UUID of a team that need to be deleted
    :return: confirmation of deletion
    """
    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj

    """request part"""
    try:
        team = Team.objects.get_or_404(teamName=teamName)
        if team.owner_user != user:  # only the owner can modify the team name
            return jsonify("Unauthorized"), 401
        team.delete()  # delete the team
        return jsonify("delete success"), 200
    except Exception as e:
        return jsonify(str(e)), 404
