from flask import Flask, jsonify, request
import json
from flask import make_response
import sys
#import algorithms
from Alloc_Algorithm._blockRand import block_randomization
from Alloc_Algorithm._simpleRand import simple_rand
#mongo db
from flask import Flask, request, Response
from database.db import initialize_db
from database.models import Team,Study, Study_SimpleRand,Study_BlockRand,Block
#import lazy dict




sys.path.append(r'/Users/David/Desktop/Research/git/SAM/codes/Alloc_Algorithm')

app = Flask(__name__)


app.config['MONGODB_SETTINGS'] = {'host': 'mongodb://localhost/test_db'}
initialize_db(app)

avaliable_allocTypes = {
    "simpleRand": Study_SimpleRand,
    "blockRand": Study_BlockRand
}



"""

avaliable_allocTypes = {"simpleRand":simple_rand, "blockRand":block_randomization}

team_2_studies = {
    'studyId': 2,
    'studyName': "s1",
    'numberParticipant': 100,
    'studyGroup': {'groupNames': ["a1", "a2", "a3"],
                   'groupRatio': [0.333, 0.333, 0.333],
                   'blockSize': 3},
    'allocType': "blockRand",
    'participants': []
}

teams = [{'teamId': 1, 'teamName': "A", "studies": []},
         {'teamId': 2, 'teamName': "B", "studies": []}]

"""



#get all the teams in the database
"""
@app.route('/api/1.0.0/team', methods=['GET'])
def get_teams():
    return {"allTeams":teams},200
"""

@app.route('/api/1.0.0/team', methods=['GET'])
def get_teams():
    teams = Team.objects().to_json()
    return Response(teams, mimetype="application/json", status=200)




#get a team by team id
@app.route('/api/1.0.0/team/<int:teamId>', methods=['GET'])
def get_team(teamId):
    team = Team.objects.get_or_404(teamId=teamId).to_json()
    return Response(team, mimetype="application/json", status=200)



#create a team
@app.route('/api/1.0.0/team', methods=['POST'])
def create_team():
    #read request
    teamData = request.get_json()
    #add to DB
    team_created = Team(**teamData).save()
    teamId = team_created.teamId
    return {'teamId': str(teamId)}, 200

#update a team
@app.route('/api/1.0.0/team/<int:teamId>', methods=['PATCH'])
def update_team():
    teamData = request.get_json()
    teamId_update = teamId
    Team.objects.get(teamId=teamId_update).update(**teamData)
    return jsonify("update success", 201)

#delete a team#
@app.route('/api/1.0.0/team/<int:teamId>', methods=['DELETE'])
def delete_team(teamId):
    Team.objects.get(teamId=teamId).delete()
    return jsonify("delete success", 200)



###creating study by allocation type###
@app.route('/api/1.0.0/team/<int:teamId>/study/<allocType>', methods = ['POST'])
def create_study(teamId,allocType):
    #get the information
    studyData = request.get_json()
    #check allocType is vaild
    #bad request if allocation not avaliable or not consistant
    if allocType not in avaliable_allocTypes or str(allocType) != studyData['allocType']:
        return jsonify("Bad allocation type", 404)
    #check if the team in database
    Team.objects.get_or_404(teamId = teamId)
    #add to Study db(by condition)
    Study = avaliable_allocTypes[allocType]
    study_created = Study(**studyData).save()
    #update studies of a Team, by teamId
    Team.objects(teamId=teamId).update_one(push__studies = study_created)

    return jsonify("create study success", 200)


###delete a study###
@app.route('/api/1.0.0/team/<int:teamId>/study/<int:studyId>', methods = ['DELETE'])
def delete_study(teamId,studyId):
    #delete study from database
    study_deleted = Study.objects.get(studyId=studyId).delete()
    #remove study from the team reference
    Team.objects(teamId=teamId).update_one(pull__studies = study_deleted)
    return jsonify("delete success", 200)




###retrive allocation or allocate a study###
@app.route('/api/1.0.0/team/<int:teamId>/study/<int:studyId>', methods = ['GET'])
def get_study(teamId,studyId):
    #test if is vaild and get allocation type
    studyGet = Study.objects.get_or_404(studyId=studyId)
    allocType = studyGet.allocType
    #get the study obejcts from db
    studyObject= Study.objects(studyId=studyId)

    # if study already allocated, retrive the previous allocation
    if studyGet.allocationSequence:
        #print(studyGet.allocationSequence)
        return Response(studyGet.to_json(), mimetype="application/json", status=200)


    #if the study not being allocated, conduct allocation
    #allocation algorithms
    if allocType == "simpleRand":
        resultSequence = simple_rand(num_participant = studyGet.numberParticipant,
                                     group_name = studyGet.studyGroupNames)
        #get the sequence
        resultSequence = resultSequence[0]
        #update
        studyObject.update_one(allocationSequence=resultSequence)
        return Response(studyObject.to_json(), mimetype="application/json", status=200)



    elif allocType == "blockRand":
        resultSequence = block_randomization(num_participant=studyGet.numberParticipant,
                                             group_name=studyGet.studyGroupNames,
                                             block_size= studyGet.studyBlockSize)
        print(resultSequence)
        #update sequence
        for i,seq in enumerate(resultSequence):
            print(seq)
            block = {i:seq}
            print(block)
            #studyObject.update_one(push__allocationSequence = seq)
            studyGet.allocationSequence.append(block)
        return Response(studyGet.to_json(), mimetype="application/json", status=200)

    elif allocType == "randBlockRand":
        return

###retrive allocation of a study###



"""
    #simple rand case
    if allocType == "simpleRand":
        numberParticipant =
        groupNames = body['studyGroup']['groupNames']
        groupRatio = body['studyGroup']['groupRatio']

        allocation = simple_rand(num_participant=numberParticipant,
                                 group_name=groupNames,
                                 seed=None, ratio_group=groupRatio)
        body['allocation'] = allocation
        study = body
        team['studies'].append(study)
        return study




    return
"""










if __name__ == '__main__':
    app.run(debug=True)
