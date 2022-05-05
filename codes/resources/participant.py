from flask import Blueprint, Response, request, jsonify
from database.db import initialize_db
from database.models import Study_Minimization, Study_Participant, User
import uuid
# import algorithms
from Alloc_Algorithm._blockRand import block_randomization
from Alloc_Algorithm._simpleRand import simple_rand
from Alloc_Algorithm._blockRand import randomized_block_randomization
from Alloc_Algorithm import Trial, Participant
# auth
from flask_jwt_extended import jwt_required, get_jwt_identity

participant = Blueprint('participant', __name__)


@participant.route('/api/1.0.0/study/<studyId>/minimizeParticipant', methods=['POST'])
@jwt_required()
def add_participant(studyId):
    """
    insert a participant to the minimization study

    :param studyId: the id of the minimization study
    :return: the participant covars and its ID
    """

    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj

    """Participant info section"""
    # get the information
    participantData = request.get_json()
    # participant covars
    participantCovarsIndex = participantData['covars']
    # participant PID
    PID = participantData['PID']

    """minimization study info section"""
    # get the study
    study = Study_Minimization.objects(studyId=studyId, add_by_user=user).get_or_404()
    # covars of the study
    studyCovars = study.covars.field_name
    # groupScores of the study
    studyGroupScores = study.groupScores
    # group names of the study
    studyGroupNames = study.studyGroupNames
    # allocation sequence
    allocationSequence = study.allocationSequence

    """validation part"""
    # check if study covars name is equal to participant covars name
    if studyCovars.keys() != participantCovarsIndex.keys() or len(studyCovars) != len(participantCovarsIndex):
        return jsonify("invalid participant covars or repeated covars", 400)
    # check if participant covars' index is vaild
    for covar, index in participantCovarsIndex.items():
        try:
            studyCovars[covar][int(index)]
        except IndexError:
            return jsonify("invalid participant covar index", 400)

    # create and save participant object
    # autogenerate uuid
    participantUUID = uuid.uuid4()
    participant_created = Study_Participant(PID=PID,
                                            participantId=participantUUID,
                                            participantCovarsIndex=participantCovarsIndex,
                                            add_by_user=user).save()

    # push the participant to the minimize study
    study.participants.append(participant_created)
    study.save()

    """allocate the participant"""
    participant_obj = Participant(ID=str(participantUUID), covars=studyCovars, covarIndex=participantCovarsIndex)
    trial_obj = Trial(Trial_name="test", group_name=studyGroupNames, covars=studyCovars, groupScore=studyGroupScores)

    # if no allocation in the minimization study
    if not allocationSequence:
        # add the first participant to the trail
        trial_obj.addParticipant(par=participant_obj)
        # get the initial allocation for the first participant
        initAllocationSequence, initGroupScores = trial_obj.minimization_trial()
        # save initial allocation sequence and its scores
        study.allocationSequence = initAllocationSequence
        study.groupScores = initGroupScores
        study.save()
        # update participant allocation info
        # find the allocation group
        """find the allocation group and assign the participant to that group"""
        allocation = None
        for group, seq in initAllocationSequence.items():
            if len(seq) > 0:
                allocation = group
                break
        participant_created.allocation = allocation
        participant_created.save()
        return Response(participant_created.to_json(), mimetype="application/json", status=200)

    # if allocation exist, allocate the additional participant
    allocatedGroup = trial_obj.minimize_and_AddParticipant(participant_obj)
    # get the updated group scores
    updatedGroupScores = trial_obj.getGroupScore()
    # append to the allocation sequence
    allocationSequence[str(allocatedGroup)].append(str(participantUUID))
    """find the allocation group and assign the participant to that group"""
    participant_created.allocation = str(allocatedGroup)
    participant_created.save()
    # update db
    study.allocationSequence = allocationSequence
    study.groupScores = updatedGroupScores
    study.save()

    return Response(participant_created.to_json(), mimetype="application/json", status=200)


@participant.route('/api/1.0.0/minimizeParticipant/<participantId>', methods=['DELETE'])
@jwt_required()
def delete_participant(participantId):
    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj

    Study_Participant.objects.get(participantId=participantId,add_by_user = user).delete()
    return jsonify("delete success", 200)
