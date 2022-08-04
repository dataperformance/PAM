import mongoengine.errors
from flask import Blueprint, Response, request, jsonify
from database.models import Study_Minimization, Study_Participant, User
from alloc_algorithms import Trial, Participant
# auth
from flask_jwt_extended import jwt_required, get_jwt_identity

participant = Blueprint('participant', __name__)


# only the team member can add the participant
@participant.route('/api/1.0.0/study/minimizeParticipant', methods=['POST'])
@jwt_required()
def minimize_participant():
    """
    insert a participant to the minimization study

    :input: studyId the id of the minimization study
    :return: the participant covars and its ID
    """

    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj

    """study validation"""
    try:
        studyId = request.get_json()['studyId']
        # get the study
        study = Study_Minimization.objects(studyId=studyId).get_or_404()
        # covars of the study
        studyCovars = study.covars.field_name
        # groupScores of the study
        studyGroupScores = study.groupScores
        # group names of the study
        studyGroupNames = study.studyGroupNames
        # allocation sequence
        allocationSequence = study.allocationSequence

        ### authority validation: only the study member can use call this request###
        member_users = study.member_users
        if user not in member_users:
            return jsonify({"msg":"Unauthorized"}), 401
        """Participant info section"""
        # get the information
        participantData = request.get_json()
        # participant covars
        participantCovarsIndex = participantData['covars']
        # participant PID
        PID = participantData['PID']

    except KeyError as KE:
        return jsonify({"msg":"Input Key Error: {}".format(str(KE))}), 404
    except Exception as e:
        return jsonify({"msg":"Please valid study"}), 404

    """participantCovarsIndex validation"""
    # check if study covars name is equal to participant covars name
    if studyCovars.keys() != participantCovarsIndex.keys() or len(studyCovars) != len(participantCovarsIndex):
        return jsonify({"msg":"invalid participant covars or repeated covars"}), 400
    # check if participant covars' index is valid
    for covar, index in participantCovarsIndex.items():
        try:
            studyCovars[covar][int(index)]
        except IndexError:
            return jsonify({"msg":"invalid participant covar index"}), 400

    """PID validation and store participant obj"""
    # create and save participant object
    try:
        participant_created = Study_Participant(PID=PID,
                                                participantCovarsIndex=participantCovarsIndex,
                                                owner_user=user,
                                                owner_study=study).save()
    except mongoengine.errors.NotUniqueError:
        return jsonify({"msg":"PID uot unique for the study"}), 409

    # push the participant to the minimize study
    study.participants.append(participant_created)
    study.save()

    """allocate the participant"""
    participant_obj = Participant(ID=str(PID), covars=studyCovars,
                                  covarIndex=participantCovarsIndex)  # use PID instead of UUID
    trial_obj = Trial(Trial_name="test", group_name=studyGroupNames, covars=studyCovars
                      , groupScore=studyGroupScores, allocation=allocationSequence)

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

    """find the allocation group and assign the participant to that group"""
    participant_created.allocation = str(allocatedGroup)
    participant_created.save()
    # update db
    study.allocationSequence = allocationSequence
    study.groupScores = updatedGroupScores
    study.save()

    return Response(participant_created.to_json(), mimetype="application/json", status=200)


# only the team member can delete the participant
@participant.route('/api/1.0.0/study/<studyId>/deleteParticipant/<PID>', methods=['DELETE'])
@jwt_required()
def delete_participant(studyId, PID):
    """
    Delete a participant of a study
    :param studyId, PID
    :return: the study after deleted
    """

    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj

    """study validation"""
    try:
        """minimization study info section"""
        # get the study
        study = Study_Minimization.objects(studyId=studyId).get_or_404()
        # groupScores of the study
        studyGroupScores = study.groupScores
        # allocation sequence
        allocationSequence = study.allocationSequence
        ### authority validation: only the study member can use call this request###
        member_users = study.member_users
        if user not in member_users:
            return jsonify({"msg":"Unauthorized"}), 401

    except Exception as e:
        return jsonify({"msg":str(e)}), 404

    """Participant info section"""
    try:
        # get the information
        participant_deleted = Study_Participant.objects.get(owner_study=study, PID=PID)
        # participant covars
        participantCovarsIndex = participant_deleted.participantCovarsIndex
        # participant PID
        # participant allocation
        allocation = participant_deleted.allocation
    except Exception as e:
        return jsonify({"msg": str(e)}), 400

    """update the study after removing the participant from the study"""
    allocationSequence[allocation].remove(PID)  # remove the participant from the allocaiton sequence

    for key, i in participantCovarsIndex.items():  # remove the participant from the group scores
        studyGroupScores[allocation][key][i] -= 1

    study.save()
    participant_deleted.delete()

    return jsonify({"msg": "delete success"}, 202)


@participant.route('/api/1.0.0/study/addParticipant', methods=['POST'])
@jwt_required()
def add_participant_manually():
    """
    Manually add participant to the minimization study
    :param studyId: the id of the minimization study
    :return: the participant covars and its ID
    """

    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj

    """study validation"""
    try:
        studyId = request.get_json()['studyId']
        # get the study
        study = Study_Minimization.objects(studyId=studyId).get_or_404()
        # covars of the study
        studyCovars = study.covars.field_name
        # groupScores of the study
        studyGroupScores = study.groupScores
        # group names of the study
        studyGroupNames = study.studyGroupNames
        # allocation sequence
        allocationSequence = study.allocationSequence
        ### authority validation: only the study member can use call this request###
        member_users = study.member_users
        if user not in member_users:
            return jsonify({"msg":"Unauthorized"}), 401

    except KeyError as KE:
        return jsonify({"msg": "Input Key Error: {}".format(str(KE))}), 404
    except Exception as e:
        return jsonify({"msg": "Please valid study"}), 404

    """Participant info section"""
    try:
        # get the information
        participantData = request.get_json()
        # participant covars
        participantCovarsIndex = participantData['covars']
        # participant PID
        PID = participantData['PID']
        # participant allocation
        allocation = participantData['allocation']
    except Exception as e:
        return jsonify({"msg": "please input participantCovarsIndex, PID and its allocation"}), 400

    """participant allocation validation"""
    if allocation not in studyGroupNames:
        return jsonify({"msg": "Invalid participant allocation"}), 400

    """participantCovarsIndex validation"""
    # check if study covars name is equal to participant covars name
    if studyCovars.keys() != participantCovarsIndex.keys() or len(studyCovars) != len(participantCovarsIndex):
        return jsonify({"msg": "invalid participant covars or repeated covars"}), 400
    # check if participant covars' index is valid
    for covar, index in participantCovarsIndex.items():
        try:
            studyCovars[covar][int(index)]
        except IndexError:
            return jsonify({"msg": "invalid participant covar index"}), 400

    """PID validation and store participant obj"""
    # create and save participant object
    try:
        participant_created = Study_Participant(PID=PID,
                                                participantCovarsIndex=participantCovarsIndex,
                                                owner_user=user,
                                                owner_study=study,
                                                allocation=allocation)

        participant_obj = Participant(ID=str(PID), covars=studyCovars,
                                      covarIndex=participantCovarsIndex)  # use PID instead of UUID
        trial_obj = Trial(Trial_name="test", group_name=studyGroupNames, covars=studyCovars,
                          groupScore=studyGroupScores,
                          allocation=allocationSequence)

        allocationSequence, GroupScores = trial_obj.allocate_participant(participant_obj, allocation)
        # update db
        study.allocationSequence = allocationSequence
        study.groupScores = GroupScores
        # push the participant to the minimize study
        study.participants.append(participant_created)
        participant_created.save()
        study.save()
    except Exception as e:
        return jsonify({"msg": "PID uot unique for the study"}), 409

    return Response(participant_created.to_json(), mimetype="application/json", status=200)
