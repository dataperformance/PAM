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





#sys.path.append(r'/Users/David/Desktop/Research/git/SAM/codes/Alloc_Algorithm')

app = Flask(__name__)


app.config['MONGODB_SETTINGS'] = {'host': 'mongodb://localhost/test_db'}
initialize_db(app)

avaliable_allocTypes = {
    "simpleRand": Study_SimpleRand,
    "blockRand": Study_BlockRand,
    "minimization": Study_Minimization,
    'randBlockRand': Study_RandBlockRand
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
    """
    :return:  {
        "teamId"
        "teamName"
        "studies"
    }
    """
    #prevent showing oid
    teams_json = []
    teams = Team.objects().exclude('id').all()
    #change oid to UUID
    for team in teams:
        teams_json.append(team.to_json())

    #teams.studies = Team.objects().exclude('id').all().get().get_studies()
    return Response(teams_json, mimetype="application/json", status=200)




#get a team by team id
@app.route('/api/1.0.0/team/<teamId>', methods=['GET'])
def get_team(teamId):
    """
    :param teamId: the UUID of a team
    :return:
    """
    #team = Team.objects.get_or_404(teamId=teamId).to_json()
    team = Team.objects(teamId = teamId).exclude('id').get_or_404()
    #if team is empty
    if not team:
        return jsonify("team not found", 404)
    return Response(team.to_json(), mimetype="application/json", status=200)



#create a team
@app.route('/api/1.0.0/team', methods=['POST'])
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

    #read request
    teamData = request.get_json()
    #add to DB
    team_created = Team(teamName = teamData['teamName']
                        ,teamId = uuid.uuid4()).save()
    #auto generate UUID4 to the teamID
    teamName = team_created.teamName
    teamId = team_created.teamId
    return {'teamId': teamId, 'teamName':teamName}, 200




#update a team by teamId
@app.route('/api/1.0.0/team/<teamId>', methods=['PATCH'])
def update_team(teamId):
    """

    :param teamId:
    :return: update teamName
    """
    teamData = request.get_json()
    teamId_update = teamId
    Team.objects.get(teamId=teamId_update).update(**teamData)
    return jsonify("update success", 201)



#delete a team#
@app.route('/api/1.0.0/team/<teamId>', methods=['DELETE'])
def delete_team(teamId):
    """
    :param teamId: the UUID of a team that need to be deleted
    :return: confirmation of deletion
    """
    Team.objects.get(teamId=teamId).delete()
    return jsonify("delete success", 200)



###creating study by allocation type###
@app.route('/api/1.0.0/team/<teamId>/study/<allocType>', methods = ['POST'])
def create_study(teamId,allocType):
    """

    :param teamId: The UUID of a team that the study belongs to
    :param allocType: A allocation type
    :return: the created study


    """
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
    #generate unique uuid
    studyId = uuid.uuid4()
    #inser UUID studyId to studyData
    studyData.update({"studyId":studyId})

    #if the allocation type is minimization, it required user to input participant
    if allocType == "minimization":
        #read covars for the minimization study
        covars = studyData['covars']
        #all participants for the minimization study
        participants = studyData['participants']
        return_participants = []
        for par_covarsIndex in participants:
            participantId = uuid.uuid4()
            par_created = Study_Participant(field_name = par_covarsIndex,participantId = participantId).save()
            return_participants.append(par_created)

        #create covar variable for the study and store it to the databse
        covars_created = Study_Covariables(field_name = covars).save()
        #create the minimization study, require participant covarsIndex
        study_created = Study(studyGroupNames = studyData['studyGroupNames'],
                              studyId = studyId,studyName = studyData['studyName'],
                              allocType = allocType,covars = covars_created,participants = return_participants).save()
        #push the study to the team we create
        Team.objects(teamId=teamId).update_one(push__studies=study_created)
        return jsonify({"studyId":studyId}, 200)

    else:
        study_created = Study(**studyData).save()
        #update studies of a Team, by teamId
        Team.objects(teamId=teamId).update_one(push__studies = study_created)

        return jsonify({"studyId":studyId}, 200)


###delete a study###
@app.route('/api/1.0.0/study/<studyId>', methods = ['DELETE'])
def delete_study(studyId):
    """

    :param studyId: the UUID of a study
    :return: the confirmation of deletion
    """
    #delete study from database
    study_deleted = Study.objects.get(studyId=studyId).delete()
    return jsonify("delete success", 200)





###retrive allocation or allocate a study###
@app.route('/api/1.0.0/study/<studyId>', methods = ['GET'])
def get_study(studyId):
    """

    :param studyId: The UUID of a study
    :return: the allocation sequence of a study, and its parameter
    """
    #test if is vaild and get allocation type
    studyGet = Study.objects.exclude('id').get_or_404(studyId=studyId)
    allocType = studyGet.allocType
    #get the study obejcts from db
    studyObject= Study.objects(studyId=studyId)

    # if study already allocated, retrive the previous allocation
    if studyGet.allocationSequence:
        return Response(studyGet.to_json(), mimetype="application/json", status=200)


    #if the study not being allocated, conduct allocation
    #allocation algorithms

    ##simple randomization case##
    if allocType == "simpleRand":
        resultSequence = simple_rand(num_participant = studyGet.numberParticipant,
                                     group_name = studyGet.studyGroupNames)
        #get the sequence
        resultSequence = resultSequence[0]
        #update
        studyGet.update(allocationSequence=resultSequence)

        #update allocation status
        studyGet.update(allocated=True)
        return Response(studyGet.to_json(), mimetype="application/json", status=200)

    ##blockRand case##
    elif allocType == "blockRand":
        resultSequence = block_randomization(num_participant=studyGet.numberParticipant,
                                             group_name=studyGet.studyGroupNames,
                                             block_size= studyGet.studyBlockSize)

        #update sequence
        for i,seq in enumerate(resultSequence):
           #print(seq)
            block = {str(i):seq}
            #studyObject.update_one(push__allocationSequence = seq)
            studyGet.allocationSequence.append(block)
            #studyGet.save()
        #update allocation status
        studyGet.update(allocated=True)
        studyGet.save()
        return Response(studyGet.to_json(), mimetype="application/json", status=200)

    ##minimization case###
    elif allocType == "minimization":
        participants = studyGet['participants']
        covars = studyGet['covars']['field_name']
        studyGroupNames = studyGet.studyGroupNames
        trial = Trial(Trial_name="test", group_name=studyGroupNames,covars=covars)
        for par in participants:
            #get the covarsIndex of a participant
            parId = par.get_id()
            covarIndex = par['field_name']
            par_obj = Participant(ID=parId,covarIndex = covarIndex,covars= covars)
            trial.addParticipant(par=par_obj)

        #return the object ID
        resultSequence = trial.minimization_trial()
        # update sequence
        for i, seq in enumerate(resultSequence):
            #print(seq)
            block = {str(i): seq}
            # studyObject.update_one(push__allocationSequence = seq)
            studyGet.allocationSequence.append(block)

        #update allocation status
        studyGet.update(allocated=True)
        #exclude object id from response

        return Response(studyGet.to_json(), mimetype="application/json", status=200)

    ##randomized block randomization##
    elif allocType == "randBlockRand":
        resultSequence = randomized_block_randomization(num_participant=studyGet.numberParticipant,
                                             group_name=studyGet.studyGroupNames,
                                             random_block_size=studyGet.studyBlockSizes)
        res = []
        for i,seq in enumerate(resultSequence):
           #print(seq)
            block = {str(i):seq}
            res.append(block)
            studyGet.allocationSequence.append(block)
        #studyGet.update(allocationSequence=res)
        #update allocation status
        studyGet.update(allocated=True)
        studyGet.save()
        return Response(studyGet.to_json(), mimetype="application/json", status=200)

###view a study parameter or allocate###
@app.route('/api/1.0.0/study/view/<studyId>', methods = ['GET'])
def view_study(studyId):
    """

    :param studyId: UUID of a study
    :return: parameter of a study
    Example:

    """
    view_object = Study.objects.exclude('id').get_or_404(studyId = studyId)
    return Response(view_object.to_json(), mimetype="application/json", status=200)










if __name__ == '__main__':
    app.run(debug=True)
