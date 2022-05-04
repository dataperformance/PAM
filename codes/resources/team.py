import json
from flask import Blueprint, Response, request, jsonify
from database.db import initialize_db
from database.models import Team, Study, Study_SimpleRand, \
    Study_BlockRand, Study_Block, Study_Minimization, Study_Covariables, Study_Participant, Study_RandBlockRand
import uuid

team = Blueprint('team', __name__)

from bson.objectid import ObjectId
def newEncoder(o):
    if type(o) == ObjectId:
        return str(o)
    return o.__str__



@team.route('/api/1.0.0/team/', defaults={'teamId': None}, methods=['GET'])
@team.route('/api/1.0.0/team/<teamId>', methods=['GET'])
def get_team(teamId):
    """
    :return:  {
        "teamId"
        "teamName"
        "studies"
    }
    """
    if teamId:
        team = Team.objects(teamId=teamId).get_or_404()
        return Response(team.to_json(), mimetype="application/json", status=200)

    teams_objs = Team.objects().all()
    teams = []
    #delete the oid from view
    for team_obj in teams_objs:
        team = json.loads(team_obj.to_json())
        teams.append(team)

    view = {'allteams':teams}
    return jsonify(view), 200


# get a team by team id
#@team.route('/api/1.0.0/team/<teamId>', methods=['GET'])
#def get_team(teamId):
#    """
#    :param teamId: the UUID of a team
#    :return:
#    """
#    # team = Team.objects.get_or_404(teamId=teamId).to_json()
#    team = Team.objects(teamId=teamId).get_or_404()
#    # if team is empty
#    if not team:
#        return jsonify("team not found", 404)
#    return Response(team.to_json(), mimetype="application/json", status=200)


# create a team
@team.route('/api/1.0.0/team', methods=['POST'])
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

    # read request
    teamData = request.get_json()
    # team id generate
    teamId = uuid.uuid4()

    # add to DB
    team_created = Team(teamName=teamData['teamName']
                        , teamId=teamId).save()
    # auto generate UUID4 to the teamID
    teamName = team_created.teamName
    teamId = team_created.teamId
    return {'teamId': teamId, 'teamName': teamName}, 200


# update a team by teamId
@team.route('/api/1.0.0/team/<teamId>', methods=['PATCH'])
def update_team(teamId):
    """

    :param teamId:
    :return: update teamName
    """
    teamData = request.get_json()
    teamId_update = teamId
    Team.objects.get(teamId=teamId_update).update(**teamData)
    return jsonify("update success", 201)


# delete a team#
@team.route('/api/1.0.0/team/<teamId>', methods=['DELETE'])
def delete_team(teamId):
    """
    :param teamId: the UUID of a team that need to be deleted
    :return: confirmation of deletion
    """
    Team.objects.get(teamId=teamId).delete()
    return jsonify("delete success", 200)
