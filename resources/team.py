import json
import mongoengine.errors
import pymongo.errors
from flask import Blueprint, Response, request, jsonify
from database.models import Team, User
import uuid
from flask_jwt_extended import jwt_required, get_jwt_identity

team = Blueprint('team', __name__)


# get a team or teams
@team.route('/api/1.0.0/team/', defaults={'teamId': None}, methods=['GET'])  # default teamId is none
@team.route('/api/1.0.0/team/<teamId>', methods=['GET'])
@jwt_required()
def get_team(teamId):
    """
    get all teams or a team by id
    input:{
    "teamId"
    }
    :return:  {
        "teamId"
        "teamName"
        "studies"
    }
    """
    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj
    teams = user.teams
    """request part"""
    if teamId:
        try:
            team = Team.objects(teamId=teamId).get_or_404()  # get a team that add by the user
            if team not in teams:
                return jsonify("Unauthorized"), 401
            return Response(team.to_json(), mimetype="application/json", status=200)
        except Exception as e:
            return jsonify("Invalid teamId"), 404

    # Team.objects(add_by_user=user).all()  # get all the teams that added by the user
    allteams = [] if not teams else [json.loads(team.to_json()) for team in teams]
    view = {'allteams': allteams}
    return jsonify(view), 200


# create a team
@team.route('/api/1.0.0/team', methods=['POST'])
@jwt_required()  # required auth
def create_team():
    """
    input: {
        "teamName":
    }

    :return: {
    "teamId":UUID,
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
                            teamId=teamId,
                            owner_user=user,
                            member_users=[user]).save()

    except mongoengine.errors.NotUniqueError as e:
        return jsonify({'msg':"teamName need to be unique"}),400
    # add team to the user

    User.objects(userId=userId).update_one(push__teams=team_created)

    teamName = team_created.teamName
    teamId = team_created.teamId

    return {'teamId': teamId, 'teamName': teamName}, 200


# update a team by teamId
@team.route('/api/1.0.0/team/<teamId>', methods=['PATCH'])
@jwt_required()
def update_team(teamId):
    """
    :input teamId:
    :return: update teamName
    """
    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj
    """request part"""

    try:
        teamName = request.get_json()['teamName']
        team = Team.objects.get_or_404(teamId=teamId)
        if team.owner_user != user:  # only the owner can modify the team name
            return jsonify({'msg':"Unauthorized"}), 401
        team.update(teamName=teamName)
    except mongoengine.errors.NotUniqueError:
        return jsonify({'msg': "teamName need to be unique"}),409
    except Exception as e:
        return jsonify({'msg':"Invalid request"}), 404

    return jsonify({'msg':"update success"}), 201


# delete a team
@team.route('/api/1.0.0/team/<teamId>', methods=['DELETE'])
@jwt_required()
def delete_team(teamId):
    """
    delete a team and its all studies
    :input teamId: the UUID of a team that need to be deleted
    :return: confirmation of deletion
    """
    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj

    """request part"""
    try:
        team = Team.objects.get_or_404(teamId=teamId)
        if team.owner_user != user:  # only the owner can modify the team name
            return jsonify("Unauthorized"), 401
        team.delete()  # delete the team
        return jsonify("delete success"), 200
    except Exception as e:
        return jsonify(str(e)), 404
