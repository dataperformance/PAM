import json
from flask import Blueprint, Response, request, jsonify
from database.db import initialize_db
from database.models import Team, Study, Study_SimpleRand, \
    Study_BlockRand, Study_Block, Study_Minimization, Study_Covariables, Study_Participant, Study_RandBlockRand, User
import uuid
from flask_jwt_extended import jwt_required, get_jwt_identity

team = Blueprint('team', __name__)


@team.route('/api/1.0.0/team/', defaults={'teamId': None}, methods=['GET'])
@team.route('/api/1.0.0/team/<teamId>', methods=['GET'])
@jwt_required()
def get_team(teamId):
    """
    get all teams or a team by id
    :return:  {
        "teamId"
        "teamName"
        "studies"
    }
    """
    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj

    """request part"""

    if teamId:
        team = Team.objects(teamId=teamId, add_by=user).get_or_404()  # get a team that add by the user
        return Response(team.to_json(), mimetype="application/json", status=200)

    teams_objs = Team.objects(add_by=user).all()  # get all the teams that added by the user
    teams = []
    # delete the oid from view
    for team_obj in teams_objs:
        team = json.loads(team_obj.to_json())
        teams.append(team)

    view = {'allteams': teams}
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
    team_created = Team(teamName=teamData['teamName']
                        , teamId=teamId,
                        add_by=user).save()  # create reference to the auth user
    # auto generate UUID4 to the teamID
    teamName = team_created.teamName
    teamId = team_created.teamId
    return {'teamId': teamId, 'teamName': teamName}, 200


# update a team by teamId
@team.route('/api/1.0.0/team/<teamId>', methods=['PATCH'])
@jwt_required()
def update_team(teamId):
    """

    :param teamId:
    :return: update teamName
    """
    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj
    """request part"""
    teamData = request.get_json()
    teamId_update = teamId
    Team.objects.get_or_404(teamId=teamId_update, add_by=user).update(**teamData)
    return jsonify("update success", 201)


# delete a team
@team.route('/api/1.0.0/team/<teamId>', methods=['DELETE'])
@jwt_required()
def delete_team(teamId):
    """
    delete a team and its all studies
    :param teamId: the UUID of a team that need to be deleted
    :return: confirmation of deletion
    """
    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj

    Team.objects.get(teamId=teamId, add_by=user).delete()  # delete the team
    return jsonify("delete success", 200)
