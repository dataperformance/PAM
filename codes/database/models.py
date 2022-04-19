from .db import db
from mongoengine import DateTimeField, StringField, ReferenceField, ListField,IntField,CASCADE,EmbeddedDocumentField,MapField,DictField
import mongoengine

class Study(db.Document):
    #each study requires a unique study Id from the user
    studyId = IntField(required=True, unique=True)
    studyName = StringField(required=True, unique=False)
    numberParticipant = IntField(required=True, unique=False)
    studyGroupNames = ListField(StringField(), required=True)
    allocType = StringField(required = True)
    participantIds = ListField(IntField(), required=False)
    meta = {'allow_inheritance': True}
    def __unicode__(self):
        return self.studyId

    def __repr__(self):
        return self.studyId


class Block(db.EmbeddedDocument):
    #seqence within a block
    blockSeq = ListField(StringField())





class Study_SimpleRand(Study):
    studyGroupRatio = ListField(IntField(), required=False)
    allocationSequence = ListField(StringField(), required=False)



class Study_BlockRand(Study):
    #each study requires a unique study Id from the user
    studyBlockSize = IntField(required=True)
    #studyGroupRatio = ListField(IntField(), required=False)
    allocationSequence = ListField(DictField())





class Team(db.Document):
    teamId = IntField(required=True, unique=True)
    teamName = StringField(required=False)
    #studies of the team
    studies = ListField(ReferenceField(Study,reverse_delete_rule=mongoengine.PULL))
