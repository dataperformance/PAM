from .db import db
from mongoengine import StringField, ReferenceField, ListField \
    , IntField, CASCADE, DictField, UUIDField, FloatField, EmailField, ValidationError
import mongoengine
import json

from flask_bcrypt import generate_password_hash, check_password_hash


def _teamName_check(name):
    special_characters = """"!@# 
    $%^&*()-+?=,<>/"""
    if any(c in special_characters for c in name):
        raise ValidationError('teamName should not include special symbols')


class Study_Participant(db.DynamicDocument):
    # should have
    PID = StringField(default=None, unique_with='owner_study')
    participantCovarsIndex = None
    allocation = StringField(default=None)
    owner_user = ReferenceField('User')  # User the participant belongs to
    owner_study = ReferenceField('Study')  # Study the participant belongs to, must unique with each minimization study

    def get_participantId(self):
        return str(self.participantId)

    def get_field(self):
        return str(self.field_name)

    # customize output json
    def to_json(self):
        data = self.to_mongo()
        # prevent showing OID
        data.pop('_id')
        data["owner_user"] = self.owner_user.email  # dereference the user by showing its email address
        data['owner_study'] = self.owner_study.studyId
        data["PID"] = self.PID
        return json.dumps(data, default=str)


class Study(db.Document):
    """study abstract class"""
    studyId = UUIDField(binary=False, required=True)
    studyName = StringField(required=True, unique=False)
    studyGroupNames = ListField(StringField(), required=True)
    allocType = StringField(required=True)
    owner_team = ReferenceField('Team')  # team the study belongs to
    owner_user = ReferenceField('User')  # User the study belongs to
    member_users = ListField(ReferenceField('User', unique=True))  # study member who can modify the study
    meta = {'allow_inheritance': True}

    def __unicode__(self):
        return self.studyId

    def __repr__(self):
        return self.studyId

    def to_json_allocation_sequence(self):
        """
        only return allocation sequence in json format
        :return: Json format
        """
        data = {"allocationSequence": self.allocationSequence,
                "allocType": self.allocType}
        return json.dumps(data)

    def to_json(self, *args):
        """
        customize to json to prevent showing Oid
        :return: json format
        """
        data = self.to_mongo()
        for arg in args:
            data.pop(str(arg))
        data.pop("_id")  # not show oid
        data.pop("_cls")  # avoid showing cls
        data['owner_team'] = self.owner_team.teamName
        data['owner_user'] = self.owner_user.email
        data['member_users'] = [member.email for member in self.member_users]  # de-reference each user
        return json.dumps(data, default=str)

    def privilege_modify_check(self, user) -> bool:
        """
        check if the user has the privilege to modify the study
        """
        return True if user == self.owner_user or user == self.owner_team.owner_user else False

    def get_member_users_email(self):
        show = [member.email for member in self.member_users]
        return show


class Study_Block(db.EmbeddedDocument):
    # sequence within a block
    blockSeq = ListField(StringField())


class Study_SimpleRand(Study):
    numberParticipant = IntField(required=True, unique=False)
    studyGroupRatio = ListField(FloatField(), required=False)
    allocationSequence = ListField(StringField(), required=False)

    def to_json_view_parameter(self):
        """
        the study parameter in json format
        :return:  json format
        """
        data = self.to_mongo()
        # remove oid
        data.pop('_id')
        # remove the allocation sequence
        data.pop('allocationSequence')
        data.pop('owner_team')
        data.pop('owner_user')
        data['member_users'] = [member.email for member in self.member_users]  # de-reference each user
        data.pop('_cls')
        return json.dumps(data)

    def to_json_simple_view(self):
        """simple view for the study"""
        return super(Study_SimpleRand, self).to_json('numberParticipant', 'studyGroupRatio', 'allocationSequence')


# block randomization data
class Study_BlockRand(Study):
    numberParticipant = IntField(required=True, unique=False)
    # each study requires a unique study Id from the user
    studyBlockSize = IntField(required=True)
    # studyGroupRatio = ListField(IntField(), required=False)
    allocationSequence = ListField(DictField())

    def to_json_view_parameter(self):
        """
        the study parameter in json format
        :return:  json format
        """
        data = self.to_mongo()
        # remove oid
        data.pop('_id')
        # remove the allocation sequence
        data.pop('allocationSequence')
        data.pop('owner_team')
        data.pop('owner_user')
        data['member_users'] = [member.email for member in self.member_users]  # de-reference each user
        data.pop('_cls')
        return json.dumps(data)

    def to_json_simple_view(self):
        return super(Study_BlockRand, self).to_json('allocationSequence', 'numberParticipant', 'studyBlockSize')


class Study_RandBlockRand(Study):
    numberParticipant = IntField(required=True, unique=False)
    studyBlockSizes = ListField(IntField(required=True))
    allocationSequence = ListField(DictField())

    def to_json_view_parameter(self):
        """
        the study parameter in json format
        :return:  json format
        """
        data = self.to_mongo()
        # remove oid
        data.pop('_id')
        # remove the allocation sequence
        data.pop('allocationSequence')
        data.pop('owner_team')
        data.pop('owner_user')
        data['member_users'] = [member.email for member in self.member_users]  # de-reference each user
        data.pop('_cls')
        return json.dumps(data)

    def to_json_simple_view(self):
        return super(Study_RandBlockRand, self).to_json('numberParticipant', 'studyBlockSizes', 'allocationSequence')


# dataframe columns and its level
class Study_Covariables(db.DynamicDocument):
    name = StringField()
    # field name is the covars name
    field_name = None


class Study_Minimization(Study):
    participants = ListField(ReferenceField(Study_Participant, reverse_delete_rule=mongoengine.PULL), required=False)
    covars = ReferenceField(Study_Covariables, required=True)
    allocationSequence = DictField(default=None)
    # the imbalance scores for the minimization allocation
    groupScores = DictField(required=False, default=None)

    # member_users = ListField(ReferenceField('User', unique=True))  # study member who can modify the study

    @staticmethod
    def participant_IndexToVar(covars, participant):
        """
        covars: the covars for the entire study
        participant: the individual participant
        return: the string value of the participant covars
        """
        covars = covars.field_name
        participantCovarsIndex = participant.participantCovarsIndex
        participantCovars = {}
        for key, value in participantCovarsIndex.items():
            participantCovars[key] = covars[key][int(value)]
        return participantCovars

    def get_participants(self):
        participants = []
        for participant in self.participants:
            participants.append({"participantId": str(participant.id),
                                 "PID": str(participant.PID),
                                 "owner_user": str(participant.owner_user.email),
                                 "covars": self.participant_IndexToVar(self.covars, participant)}, )
        return participants

    def to_json(self):
        data = self.to_mongo()
        data["participants"] = self.get_participants()
        data['covars'] = self.covars.field_name
        data.pop('_id')  # prevent showing OID
        data['owner_user'] = self.owner_user.email
        data['owner_team'] = self.owner_team.teamName
        data['member_users'] = [member.email for member in self.member_users]  # de-reference each user
        data.pop('_cls')
        return json.dumps(data, default=str)

    def to_json_allocation_sequence(self):
        """
        only return allocation sequence in json format
        :return: Json format
        """
        data = {"allocationSequence": self.allocationSequence,
                "allocType": self.allocType}
        return json.dumps(data)

    def to_json_view_parameter(self):
        """
        the study parameter in json format
        :return:  json format(including _cls name, study UUID, study Name,
        study group names, allocation type, participant info, imbalance scores)
        """
        data = self.to_mongo()
        # remove oid
        data.pop('_id')
        data.pop('_cls')
        data['owner_user'] = self.owner_user.email
        data['owner_team'] = self.owner_team.teamName
        # dereference participant and covars
        data['participants'] = self.get_participants()
        data['covars'] = self.covars.field_name

        return json.dumps(data, default=str)

    def privilege_modify_check(self, user) -> bool:
        """check if the user can modify this study"""
        return user in self.member_users

    def to_json_simple_view(self):
        """default"""
        exclude = ['covars']
        if self.allocationSequence:
            exclude.append("allocationSequence")
        if self.groupScores:
            exclude.append("groupScores")
        if self.participants:
            exclude.append("participants")
        return super(Study_Minimization, self).to_json(*exclude)



class Study_StratBlockRand(Study):
    numberParticipant = IntField(required=True, unique=False)
    covars = ReferenceField(Study_Covariables, required=True)
    studyBlockSize = IntField(required=True)
    allocationSequence = ListField(DictField())

    def to_json_view_parameter(self):
        """
        the study parameter in json format
        :return:  json format
        """
        data = self.to_mongo()
        # remove oid
        data.pop('_id')
        # remove the allocation sequence
        data.pop('allocationSequence')
        data.pop('owner_team')
        data.pop('owner_user')
        data['member_users'] = [member.email for member in self.member_users]  # de-reference each user
        data.pop('_cls')
        return json.dumps(data)


class Team(db.Document):
    # teamName = UUIDField(binary=False, required=True)
    teamName = StringField(required=True, unique=True, validation=_teamName_check)
    # studies of the team
    studies = ListField(ReferenceField(Study, reverse_delete_rule=mongoengine.PULL, dbref=True))
    owner_user = ReferenceField('User')  # only one owner for a team
    member_users = ListField(ReferenceField('User', unique=True))  # team member array

    def delete_all_studies(self):
        for study in self.studies:
            study.delete()

        return

    def get_id(self):
        return str(self.pk)

    def get_studies(self):
        studies = []
        for study in self.studies:
            studies.append({"studyId": str(study.studyId),
                            "allocType": str(study.allocType),
                            "owner_user": str(study.owner_user.email),
                            "member_users": study.get_member_users_email()})
        return studies

    def to_json(self):
        data = self.to_mongo()
        data["studies"] = self.get_studies()
        # prevent showing OID
        data.pop('_id')
        data['owner_user'] = self.owner_user.email
        data['member_users'] = [member.email for member in self.member_users]
        return json.dumps(data, default=str)


# if a team is deleted, its studies is deleted as well
Team.register_delete_rule(Study, 'owner_team', CASCADE)


# users
class User(db.Document):
    email = EmailField(required=True, unique=True)
    password = StringField(required=True, min_length=6)
    userId = StringField(binary=False, required=True, unique=True)
    teams = ListField(ReferenceField(Team, reverse_delete_rule=mongoengine.PULL), required=False, default=None)
    studies = ListField(ReferenceField(Study, reverse_delete_rule=mongoengine.PULL), required=False, default=None)

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)


# if user deleted, its team is deleted as well(need to change)
User.register_delete_rule(Team, 'teams', CASCADE)
