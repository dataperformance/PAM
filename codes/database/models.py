from .db import db
from mongoengine import DateTimeField, StringField, ReferenceField, ListField\
    ,IntField,CASCADE,EmbeddedDocumentField,MapField,DictField,UUIDField,BooleanField
import mongoengine
import json
import bson.json_util as json_util

class Study_Participant(db.DynamicDocument):
    #should have
    participantName = StringField(default="None")
    participantId = UUIDField(binary=False,required=True)

    def get_id(self):
        return str(self.pk)
    def get_participantId(self):
        return str(self.participantIdp)
    def get_field(self):
        return str(self.field_name)



class Study(db.Document):
    #each study requires a unique study Id from the user
    studyId = UUIDField(binary=False,required=True)
    studyName = StringField(required=True, unique=False)
    studyGroupNames = ListField(StringField(), required=True)
    allocType = StringField(required = True)
    allocated = BooleanField(default=False)

    meta = {'allow_inheritance': True}
    def __unicode__(self):
        return self.studyId

    def __repr__(self):
        return self.studyId


class Study_Block(db.EmbeddedDocument):
    #seqence within a block
    blockSeq = ListField(StringField())





class Study_SimpleRand(Study):
    numberParticipant = IntField(required=True, unique=False)
    studyGroupRatio = ListField(IntField(), required=False)
    allocationSequence = ListField(StringField(), required=False)


#block randomization data
class Study_BlockRand(Study):
    numberParticipant = IntField(required=True, unique=False)
    #each study requires a unique study Id from the user
    studyBlockSize = IntField(required=True)
    #studyGroupRatio = ListField(IntField(), required=False)
    allocationSequence = ListField(DictField())


class Study_RandBlockRand(Study):
    numberParticipant = IntField(required=True, unique=False)
    studyBlockSizes = ListField(IntField(required=True))
    allocationSequence = ListField(DictField())



#dataframe columns and its level
class Study_Covariables(db.DynamicDocument):
    name = StringField()



class Study_Minimization(Study):
    participants = ListField(ReferenceField(Study_Participant, reverse_delete_rule=mongoengine.PULL),required=False)
    covars = ReferenceField(Study_Covariables,required=True)
    allocationSequence = ListField(DictField())

    def get_participants(self):
        participants = []
        for participant in self.participants:
            participants.append({"participantId":str(participant.participantId),
                            "covars_index": participant.field_name})
        return participants


    def to_json(self):
        data = self.to_mongo()
        data["participants"] = self.get_participants()
        data['covars']  = self.covars.field_name
        return json.dumps(data)




class Team(db.Document):
    teamId = UUIDField(binary=False, required=True)

    teamName = StringField(required=False)
    #studies of the team
    studies = ListField(ReferenceField(Study,reverse_delete_rule=mongoengine.PULL,dbref=True))

    def get_id(self):
        return str(self.pk)

    def get_studies(self):
        studies = []
        for study in self.studies:
            studies.append({"studyId":str(study.studyId),
                            "allocType": str(study.allocType),
                            "allocatedStatus" : str(study.allocated)})
        return studies

    def to_json(self):
        data = self.to_mongo()
        data["studies"] = self.get_studies()
        return json.dumps(data)