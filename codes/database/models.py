from .db import db
from mongoengine import DateTimeField, StringField, ReferenceField, ListField \
    , IntField, CASCADE, EmbeddedDocumentField, MapField, DictField, UUIDField, FloatField, EmailField
import mongoengine
import json

from flask_bcrypt import generate_password_hash, check_password_hash


class Study_Participant(db.DynamicDocument):
    # should have
    PID = StringField(default=None)
    participantId = UUIDField(binary=False, required=True)
    participantCovarsIndex = None
    allocation = StringField(default=None)
    add_by_user = ReferenceField('User')

    def get_participantId(self):
        return str(self.participantId)

    def get_field(self):
        return str(self.field_name)

    # customize output json
    def to_json(self):
        data = self.to_mongo()
        # prevent showing OID
        data.pop('_id')
        data["PID"] = self.PID
        return json.dumps(data, default=str)

    def __unicode__(self):
        return self.participantId


class Study(db.Document):
    # each study requires a unique study Id from the user
    studyId = UUIDField(binary=False, required=True)
    studyName = StringField(required=True, unique=False)
    studyGroupNames = ListField(StringField(), required=True)
    allocType = StringField(required=True)
    add_by_team = ReferenceField('Team') # team the study belongs to
    add_by_user = ReferenceField('User') # User the study belongs to

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

    def to_json(self):
        """
        customize to json to prevent showing Oid
        :return: json format
        """
        data = self.to_mongo()
        data.pop("_id")#not show oid
        data.pop("add_by_user")# not show the user info
        data.pop("add_by_team")# not show the team info
        return json.dumps(data, default=str)


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
        data.pop('add_by_team')
        data.pop('add_by_user')
        return json.dumps(data)


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
        data.pop('add_by_team')
        data.pop('add_by_user')
        return json.dumps(data)


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
        data.pop('add_by_team')
        data.pop('add_by_user')
        return json.dumps(data)


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

    def get_participants(self):
        participants = []
        for participant in self.participants:
            participants.append({"participantId": str(participant.participantId),
                                 "covarsIndex": participant.participantCovarsIndex})
        return participants

    def to_json(self):
        data = self.to_mongo()
        data["participants"] = self.get_participants()
        data['covars'] = self.covars.field_name
        # prevent showing OID
        data.pop('_id')
        data.pop('add_by_team')
        data.pop('add_by_user')
        return json.dumps(data, default=str)

    def to_json_view_parameter(self):
        """
        the study parameter in json format
        :return:  json format(including _cls name, study UUID, study Name,
        study group names, allocation type, participant info, imbalance scores)
        """
        data = self.to_mongo()
        # remove oid
        data.pop('_id')
        data.pop('add_by_team')
        data.pop('add_by_user')
        # remove the allocation sequence if it exist
        data.pop('allocationSequence') if self.allocationSequence else data
        # dereference participant and covars
        data['participants'] = self.get_participants()
        data['covars'] = self.covars.field_name

        return json.dumps(data, default=str)


class Team(db.Document):
    teamId = UUIDField(binary=False, required=True)
    teamName = StringField(required=False)
    # studies of the team
    studies = ListField(ReferenceField(Study, reverse_delete_rule=mongoengine.PULL, dbref=True))
    add_by = ReferenceField('User')

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
                            "allocType": str(study.allocType)})
            # "allocatedStatus" : str(study.allocated)})
        return studies

    def to_json(self):
        data = self.to_mongo()
        data["studies"] = self.get_studies()
        # prevent showing OID
        data.pop('_id')
        # prevent showing the user oid
        data.pop('add_by')
        return json.dumps(data, default=str)


# if a team is deleted, its studies is deleted as well
Team.register_delete_rule(Study, 'add_by', CASCADE)


# users
class User(db.Document):
    email = EmailField(required=True, unique=True)
    password = StringField(required=True, min_length=6)
    userId = StringField(binary=False, required=True,unique=True)
    teams = ListField(ReferenceField(Team, reverse_delete_rule=mongoengine.PULL), required=False, default=None)

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)


# if user deleted, its team is deleted as well
User.register_delete_rule(Team, 'add_by', CASCADE)
