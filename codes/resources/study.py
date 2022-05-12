from flask import Blueprint, Response, request, jsonify
from database.db import initialize_db
from database.models import Team, Study, Study_SimpleRand, \
    Study_BlockRand, Study_Block, Study_Minimization, Study_Covariables, Study_Participant, Study_RandBlockRand, User, \
    Study_StratBlockRand
import uuid
# import algorithms
from Alloc_Algorithm._blockRand import block_randomization
from Alloc_Algorithm._simpleRand import simple_rand
from Alloc_Algorithm._blockRand import randomized_block_randomization
from Alloc_Algorithm._stratBlockRand import strat_blcok_randomization
from Alloc_Algorithm import Trial, Participant
from flask_jwt_extended import jwt_required, get_jwt_identity

study = Blueprint('study', __name__)

# the available
available_allocTypes = {
    "simpleRand": Study_SimpleRand,
    "blockRand": Study_BlockRand,
    "minimization": Study_Minimization,
    'randBlockRand': Study_RandBlockRand,
    "stratBlockRand": Study_StratBlockRand
}


###creating study by allocation type###
@study.route('/api/1.0.0/team/<teamId>/study', methods=['POST'])
@jwt_required()
def create_study(teamId):
    """

    :param teamId: The UUID of a team that the study belongs to
    :param allocType: A allocation type
    :return: the created study


    """
    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj

    # get the information
    studyData = request.get_json()
    """allocation type validation"""
    try:
        allocType = studyData['allocType']
        # bad request if allocation not available or not consistent
        if allocType not in available_allocTypes or str(allocType) != studyData['allocType']:
            return jsonify("Bad allocation type", 404)
    except Exception as e:
        return jsonify("please input allocType", 400)

    # check if the user have create the team in database, and find the team Oid
    try:
        OID = Team.objects.get(teamId=teamId, add_by_user=user).id
    except Exception as e:
        return jsonify("please check the teamId", 404)
    # add to Study db(by condition)
    Study = available_allocTypes[allocType]
    """generate unique study uuid"""
    studyId = uuid.uuid4()

    # if the allocation type is minimization
    if allocType == "minimization":
        """input validation"""
        try:
            covars = studyData['covars']
            studyGroupNames = studyData['studyGroupNames']
            studyName = studyData['studyName']
        except Exception:
            return jsonify("minimization Input not correct", 400)
        # create covar variable for the study and store it to the database
        covars_created = Study_Covariables(field_name=covars).save()
        """create the minimization study, require participant covarsIndex"""
        study_created = Study(studyGroupNames=studyGroupNames,
                              studyId=studyId,
                              studyName=studyName,
                              allocType=allocType,
                              covars=covars_created,
                              add_by_team=OID,
                              add_by_user=user).save()  # , participants=return_participants).save()
        # push the study to the team we create
        Team.objects(teamId=teamId).update_one(push__studies=study_created)
        # return jsonify({"studyId": studyId}, 200)
        return Response(study_created.to_json(), mimetype="application/json", status=200)

    # if simpleRand
    elif allocType == "simpleRand":
        """input validation"""
        try:
            numberParticipant = int(studyData['numberParticipant'])
            studyGroupNames = studyData['studyGroupNames']
            studyName = studyData['studyName']
            studyGroupRatio = studyData['studyGroupRatio']
        except Exception:
            return jsonify("simpleRand Input not correct", 400)
        """Create and save the simple Rand study"""
        study_created = Study(studyGroupNames=studyGroupNames,
                              numberParticipant=numberParticipant,
                              allocType=allocType,
                              studyId=studyId,
                              studyName=studyName,
                              studyGroupRatio=studyGroupRatio,
                              add_by_team=OID,
                              add_by_user=user).save()

        # update studies of a Team, by teamId
        Team.objects(teamId=teamId).update_one(push__studies=study_created)

        """simple randomization"""
        # resultSequence = seq, seed
        resultSequence = simple_rand(num_participant=numberParticipant,
                                     group_name=studyGroupNames,
                                     ratio_group=studyGroupRatio)
        # get the allocation sequence and seed
        allocationSequence, seed = resultSequence
        """update the study"""
        study_created.allocationSequence = allocationSequence
        study_created.save()

        return Response(study_created.to_json(), mimetype="application/json", status=200)

    # if blockRand
    elif allocType == "blockRand":
        """input validation"""
        try:
            numberParticipant = int(studyData['numberParticipant'])
            studyGroupNames = studyData['studyGroupNames']
            studyName = studyData['studyName']
            studyBlockSize = int(studyData['studyBlockSize'])
        except Exception as e:
            print(e)
            return jsonify("blockRand Input not correct", 400)

        """Create and save the block Rand study"""
        study_created = Study(studyGroupNames=studyGroupNames,
                              numberParticipant=numberParticipant,
                              allocType=allocType,
                              studyId=studyId,
                              studyName=studyName,
                              studyBlockSize=studyBlockSize,
                              add_by_team=OID,
                              add_by_user=user).save()
        # update studies of a Team, by teamId
        Team.objects(teamId=teamId).update_one(push__studies=study_created)

        """blockRand"""
        resultSequence = block_randomization(num_participant=numberParticipant,
                                             group_name=studyGroupNames,
                                             block_size=studyBlockSize)

        # update sequence
        for i, seq in enumerate(resultSequence):
            block = {str(i): seq}
            study_created.allocationSequence.append(block)

        # update allocation
        study_created.save()

        return Response(study_created.to_json(), mimetype="application/json", status=200)

    # if rand block rand
    elif allocType == "randBlockRand":
        """input validation"""
        try:
            numberParticipant = int(studyData['numberParticipant'])
            studyGroupNames = studyData['studyGroupNames']
            studyName = studyData['studyName']
            studyBlockSizes = studyData['studyBlockSizes']
        except Exception as e:
            print(e)
            return jsonify("rand blockRand Input not correct", 400)

        """Create and save the rand block Rand study"""
        study_created = Study(studyGroupNames=studyGroupNames,
                              numberParticipant=numberParticipant,
                              allocType=allocType,
                              studyId=studyId,
                              studyName=studyName,
                              studyBlockSizes=studyBlockSizes,
                              add_by_team=OID,
                              add_by_user=user).save()
        # update studies of a Team, by teamId
        Team.objects(teamId=teamId).update_one(push__studies=study_created)
        """rand blockRand"""
        resultSequence = randomized_block_randomization(num_participant=numberParticipant,
                                                        group_name=studyGroupNames,
                                                        random_block_size=studyBlockSizes)
        # update the allocation sequence
        res = []
        for i, seq in enumerate(resultSequence):
            block = {str(i): seq}
            res.append(block)
            study_created.allocationSequence.append(block)
        study_created.save()
        return Response(study_created.to_json(), mimetype="application/json", status=200)

    elif allocType == "stratBlockRand":
        """input validation"""
        try:
            numberParticipant = int(studyData['numberParticipant'])
            studyGroupNames = studyData['studyGroupNames']
            studyName = studyData['studyName']
            studyBlockSize = studyData['studyBlockSize']
            covars = studyData['covars']
        except Exception as e:
            print(e)
            return jsonify("stratblockRand Input not correct", 400)

        """stratblockRand"""
        resultSequence = strat_blcok_randomization(num_participant=numberParticipant,
                                                   group_name=studyGroupNames,
                                                   block_size=studyBlockSize,
                                                   covars=covars)

        """Create and save the strat block Rand study"""
        study_created = Study(studyGroupNames=studyGroupNames,
                              numberParticipant=numberParticipant,
                              allocType=allocType,
                              studyId=studyId,
                              studyName=studyName,
                              studyBlockSize=studyBlockSize,
                              add_by_team=OID,
                              add_by_user=user,
                              covars=covars).save()
        # update studies of a Team, by teamId
        Team.objects(teamId=teamId).update_one(push__studies=study_created)

        # update sequence
        for key in resultSequence.keys():
            dic = {}
            for j in key:
                dic[j[0]] = str(j[1])

            block = {"stratum": dic,
                     "sequence": resultSequence[key]}
            study_created.allocationSequence.append(block)

        # update allocation
        study_created.save()

        return Response(study_created.to_json(), mimetype="application/json", status=200)

    else:
        jsonify("error occur", 404)


@study.route('/api/1.0.0/study/<studyId>', methods=['DELETE'])
@jwt_required()
def delete_study(studyId):
    """
    :param studyId: the UUID of a study
    :return: the confirmation of deletion
    """
    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj

    # delete study from database
    study_deleted = Study.objects.get_or_404(studyId=studyId, add_by_user=user).delete()
    return jsonify("delete success", 200)


###retrive allocation or allocate a study###
@study.route('/api/1.0.0/study/<studyId>', methods=['GET'])
@jwt_required()
def get_study(studyId):
    """
    get the allocation of a created study
    :param studyId: The UUID of a study
    :return: the allocation sequence of a study, and its parameter
    """
    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj

    # test if is valid and get allocation type
    studyGet = Study.objects(studyId=studyId, add_by_user=user).get_or_404()
    # get the study object from db
    # studyObject = Study.objects(studyId=studyId)

    return Response(studyGet.to_json_allocation_sequence(), mimetype="application/json", status=200)


@study.route('/api/1.0.0/study/view/<studyId>', methods=['GET'])
@jwt_required()
def view_study_parameter(studyId):
    """
    View a study parameter

    :param studyId: UUID of a study
    :return: parameter of a study
    Example:

    """
    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj

    view_object = Study.objects.get_or_404(studyId=studyId, add_by_user=user)
    return Response(view_object.to_json_view_parameter(), mimetype="application/json", status=200)
