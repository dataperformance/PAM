from flask import Blueprint, Response, request, jsonify
from database.models import Team, Study, Study_SimpleRand, \
    Study_BlockRand, Study_Block, Study_Minimization, Study_Covariables, Study_Participant, Study_RandBlockRand, User, \
    Study_StratBlockRand
import uuid, json
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
@study.route('/api/1.0.0/team/study', methods=['POST'])
@jwt_required()
def create_study():
    """

    :param teamName: The UUID of a team that the study belongs to
    :param allocType: A allocation type
    :return: the created study


    """

    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj
    study_created = None
    # get the information
    """request body"""
    try:
        studyData = request.get_json()
        teamName = studyData['teamName']
        allocType = studyData['allocType']
        # bad request if allocation not available or not consistent
        if allocType not in available_allocTypes or str(allocType) != studyData['allocType']:
            return jsonify("Invalid allocation type", 404)

        team = Team.objects.get(teamName=teamName)

        if user not in team.member_users:  # check if user is in the team
            return jsonify("unauthorized"), 401
        # check if the user have create the team in database, and find the team Oid
        team_OID = team.id
    except KeyError as KE:
        return jsonify({'msg': "key Error: {}".format(str(KE))}), 400
    except Team.DoesNotExist:
        return jsonify({'msg': "teamName is invalid"}), 400
    except Exception as e:
        return jsonify({'msg': "ERROR: {}".format(str(e))}), 400

    # add to Study db(by condition)
    Study = available_allocTypes[allocType]
    """generate unique study uuid"""
    studyId = uuid.uuid4()
    try:
        # if the allocation type is minimization
        if allocType == "minimization":
            """input validation"""
            covars = studyData['covars']
            studyGroupNames = studyData['studyGroupNames']
            studyName = studyData['studyName']
            # create covar variable for the study and store it to the database
            covars_created = Study_Covariables(field_name=covars).save()
            """create the minimization study, require participant covarsIndex"""
            study_created = Study(studyGroupNames=studyGroupNames,
                                  studyId=studyId,
                                  studyName=studyName,
                                  allocType=allocType,
                                  covars=covars_created,
                                  owner_team=team_OID,
                                  owner_user=user,
                                  member_users=[user])

        # if simpleRand
        elif allocType == "simpleRand":
            numberParticipant = int(studyData['numberParticipant'])
            studyGroupNames = studyData['studyGroupNames']
            studyName = studyData['studyName']
            studyGroupRatio = studyData['studyGroupRatio']
            """Create and save the simple Rand study"""
            study_created = Study(studyGroupNames=studyGroupNames,
                                  numberParticipant=numberParticipant,
                                  allocType=allocType,
                                  studyId=studyId,
                                  studyName=studyName,
                                  studyGroupRatio=studyGroupRatio,
                                  owner_team=team_OID,
                                  owner_user=user,
                                  member_users=[user])
            """simple randomization and validation"""
            resultSequence = simple_rand(num_participant=numberParticipant,
                                         group_name=studyGroupNames,
                                         ratio_group=studyGroupRatio)
            # get the allocation sequence and seed
            allocationSequence, seed = resultSequence
            """update the study"""
            study_created.allocationSequence = allocationSequence

        # if blockRand
        elif allocType == "blockRand":
            """input validation"""
            numberParticipant = int(studyData['numberParticipant'])
            studyGroupNames = studyData['studyGroupNames']
            studyName = studyData['studyName']
            studyBlockSize = int(studyData['studyBlockSize'])
            """Create and save the block Rand study"""
            study_created = Study(studyGroupNames=studyGroupNames,
                                  numberParticipant=numberParticipant,
                                  allocType=allocType,
                                  studyId=studyId,
                                  studyName=studyName,
                                  studyBlockSize=studyBlockSize,
                                  owner_team=team_OID,
                                  owner_user=user,
                                  member_users=[user])
            """blockRand"""

            resultSequence = block_randomization(num_participant=numberParticipant,
                                                 group_name=studyGroupNames,
                                                 block_size=studyBlockSize)
            # update sequence
            for i, seq in enumerate(resultSequence):
                block = {str(i): seq}
                study_created.allocationSequence.append(block)

        # if rand block rand
        elif allocType == "randBlockRand":
            numberParticipant = int(studyData['numberParticipant'])
            studyGroupNames = studyData['studyGroupNames']
            studyName = studyData['studyName']
            studyBlockSizes = studyData['studyBlockSizes']
            """Create and save the rand block Rand study"""
            study_created = Study(studyGroupNames=studyGroupNames,
                                  numberParticipant=numberParticipant,
                                  allocType=allocType,
                                  studyId=studyId,
                                  studyName=studyName,
                                  studyBlockSizes=studyBlockSizes,
                                  owner_team=team_OID,
                                  owner_user=user,
                                  member_users=[user])  # .save()
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

        elif allocType == "stratBlockRand":
            """input validation"""

            numberParticipant = int(studyData['numberParticipant'])
            studyGroupNames = studyData['studyGroupNames']
            studyName = studyData['studyName']
            studyBlockSize = studyData['studyBlockSize']
            covars = studyData['covars']

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
                                  owner_team=team_OID,
                                  owner_user=user,
                                  covars=covars,
                                  member_users=[user])
            # update sequence
            for key in resultSequence.keys():
                dic = {}
                for j in key:
                    dic[j[0]] = str(j[1])

                block = {"stratum": dic,
                         "sequence": resultSequence[key]}
                study_created.allocationSequence.append(block)

    except AssertionError as ms:
        return jsonify({'msg': str(ms)}), 400
    except KeyError as KE:
        return jsonify({'msg': "key Error: {}".format(str(KE))}), 400
    except Exception as e:
        return jsonify({'msg': "ERROR: {}".format(str(e))}), 400

    study_created.save()
    Team.objects(teamName=teamName).update_one(push__studies=study_created)
    user.update(add_to_set__studies=study_created)
    return Response(study_created.to_json(), mimetype="application/json", status=200)


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

    """studyId validation"""
    try:
        # delete study from database
        study_deleted = Study.objects.get_or_404(studyId=studyId)
        # if study_deleted.owner_user != user :  # only allow if the user is the owner or the team owner
        # return jsonify("unauthorized"), 401
        if not study_deleted.privilege_modify_check(user):
            return jsonify("unauthorized"), 401

        if str(study_deleted._cls) == "Study.Study_Minimization":
            # if deleting minimization study, delete all the
            # participant that belong to the study
            Study_Participant.objects(owner_study=study_deleted).delete()
            study_deleted.covars.delete()
            study_deleted.delete()
        else:
            study_deleted.delete()
        return jsonify("delete success", 200)
    except Exception as e:
        return jsonify(str(e)), 404


###retrive allocation or allocate a study###
@study.route('/api/1.0.0/study/<studyId>', methods=['GET'])  # change to post
@jwt_required()
def get_study(studyId):
    """
    get the allocation of a created study(only the study member)
    :input studyId: The UUID of a study
    :return: the allocation sequence of a study
    """
    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj
    user_studies = user.studies
    """studyId validation"""
    try:
        studyGet = Study.objects(studyId=studyId).get_or_404()
        if user_studies is None or studyGet not in user_studies:  # check if the user is authorized
            return jsonify("unauthorized"), 401
        return Response(studyGet.to_json(), mimetype="application/json", status=200)
    except Study.DoesNotExist:
        return jsonify({"msg": "Invalid studyId"}), 404
    except Exception as e:
        return jsonify({'msg': "ERROR: {}".format(str(e))}), 400


# obsolete
@study.route('/api/1.0.0/study/view/<studyId>', methods=['GET'])
@jwt_required()
def view_study_parameter(studyId):
    """
    View a study parameter(only the study member)

    :param studyId: UUID of a study
    :return: parameter of a study
    Example:

    """
    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj

    """studyId validation"""
    try:
        view_object = Study.objects.get_or_404(studyId=studyId)
        user_studies = user.studies
        if user_studies is None or view_object not in user_studies:  # check if the user is authorized
            return jsonify("Unauthorized"), 401

        return Response(view_object.to_json_view_parameter(), mimetype="application/json", status=200)
    except Exception as e:
        return jsonify(str(e)), 404


@study.route('/api/1.0.0/study/all', methods=['GET'])  # change to post
@jwt_required()
def get_all_studies():
    """
    get all the studies whose owner is the current user
    :return: all the studies
    """
    """auth part"""
    userId = get_jwt_identity()  # the user uuid
    user = User.objects.get_or_404(userId=userId)  # find the user obj
    """studyId validation"""
    try:
        studiesGet = user.studies
        allstudies = [] if not studiesGet else [json.loads(studyGet.to_json_simple_view()) for studyGet in studiesGet]
    except Exception as e:
        return jsonify(str(e))
    return jsonify({'allstudies': allstudies}), 200
