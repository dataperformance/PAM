import pandas as pd
from ._simpleRand import simple_rand as SR
from ._blockRand import block_randomization as BR, \
    randomized_block_randomization as RBR
from ._minimization import minimization as MZ, \
    minimize as MINI
from ._Stratify import stratify


class Participant:
    """ID can be string(name of participant)

    ###covars should be the dictionary.###
    e.g.
        {'sex': ["male","female"], "site": ["1","2"],"age_group": ["1","2","3"]}

    ###covarIndex should be the dictionary that its value is index(int) map the value in covars###
    e.g.
        {'sex': 0, "site": 1,"age_group": 1}   ===> "male", "site 1", "age_group 2"

    """

    def __init__(self, ID, covars, covarIndex):
        # ID have to be unique
        self.ID = ID
        self.aloc = "Not Assigned"
        self.covarIndex = covarIndex
        self.covar = {}
        # Initiate the paticipant covars as a dictionary
        for key, value in covars.items():
            index_value = covarIndex[key]
            string_value = value[index_value]
            self.covar[key] = string_value

        # factors, which is nested dictionary type with {covars:{level name: level index}}
        """e.g. {'sex': {'male': 0, 'female': 1}, 'site': {'1': 0, '2': 1}, 'age_group': {'1': 0, '2': 1, '3': 2}}"""
        self.factors = {}
        for var, factors in covars.items():
            i = 0
            self.factors[var] = {}
            for level in factors:
                self.factors[var][level] = i
                i += 1

    def setID(self, ID):
        self.ID = ID

    def getID(self):
        return self.ID

    def setAloc(self, aloc):
        self.aloc = aloc

    def getAloc(self):
        return self.aloc

    def getCovars(self):
        return self.covar

    def getCovarsIndex(self):
        return self.covarIndex

    def getVar(self, Var_name):
        return self.covar[Var_name]

    def __str__(self):
        return "undecided"


class Trial:
    """
    Trial_name: name of trail
    group_name: list of group name
    covars: level of columns and column name
        e.g. {'sex': ["male","female"], "site": ["1","2"],"age_group": ["1","2","3"]}
    """

    def __init__(self, Trial_name, group_name, covars, groupScore=None, allocation={}):
        self.Trial_name = Trial_name
        self.pars = []
        self.allocation = allocation  # dictionary type, used for minimization
        self.__groupScore = groupScore

        # levels = []
        # the value of the trail dataframe
        vars = []
        for key, value in covars.items():
            # levels.append(len(value))
            vars.append(key)

        # number of levels in each vars, stored in the list form
        # dataframe of the trail
        self.df = pd.DataFrame(columns=vars)

        # input covars and stores it as factors, which is nested dictionary type with {covars:{level name: level index}}
        self.factors = {}
        for var, factors in covars.items():
            i = 0
            self.factors[var] = {}
            for level in factors:
                self.factors[var][level] = i
                i += 1
        # group_name  is the vector of string type, the name of study groups(check length of group_name>= 2 & equal
        # to the length of ratio_group)
        self.group_name = group_name

    def getTrial_name(self):
        return self.Trial_name

    def setTrial_name(self, name):
        self.Trial_name = name

    def addParticipant(self, par):
        self.pars.append(par)
        par.covar["ID"] = par.getID()
        self.df = self.df.append(par.covar, ignore_index=True)

    def getParticipants(self):
        return self.pars

    def getParticipantByID(self, ID):
        # assume it is in order from 0 to current
        return self.pars[ID]

    def getParticipantID(self):
        return [i.getID() for i in self.pars]

    def getParticipantNum(self):
        return len(self.pars)

    def setGroup_name(self, group_name):
        self.group_name = group_name

    def getGroup_name(self):
        return self.group_name

    def getDataframe(self):
        return self.df

    def print_dataframe(self):
        return print(self.df)

    def getAllocation(self):
        return self.allocation

    def setAllocation(self, allocation):
        self.allocation = allocation

    def updateGroupScore(self, group_score):
        self.__groupScore = group_score

    def updateAllocation(self, alloc_name, participantId):
        self.allocation[alloc_name].append(participantId)

    def viewGroupScore(self):
        return print(self.__groupScore)

    def getGroupScore(self):
        return self.__groupScore

    ###simple randomization###
    # option1:generate the simple randomization by providing the number of participant and names of arm
    def simple_rand(num_participant, group_name, seed=None, ratio_group=None):
        return SR(num_participant, group_name, seed, ratio_group)

    # option2:generate the simple randomization from the providing trial
    def simple_rand_participant(self, seed=None, ratio_group=None):
        num_participant = self.getParticipantNum()
        group_name = self.getGroup_name()
        return SR(num_participant, group_name, seed, ratio_group)

    ###block randomization###
    # option 1: generate the block randomization by providing the number of participant, group names, block size
    @staticmethod
    def block_rand(num_participant, group_name, block_size):
        return BR(num_participant, group_name, block_size)

    # option2:
    def block_rand_participant(self, block_size):
        num_participant = self.getParticipantNum()
        group_name = self.getGroup_name()
        return BR(num_participant, group_name, block_size)

    # ##Randomized block randomization### option 1:generate the block randomization by providing the number of
    # participant, group names, list of avaliable block sizes
    @staticmethod
    def rand_block_rand(num_participant, group_name, random_block_size):
        return RBR(num_participant, group_name, random_block_size)

    # option 2: generate the simple randomization from the providing trial with input  list of avaliable block sizes
    def rand_block_rand_participant(self, random_block_size):
        num_participant = self.getParticipantNum()
        group_name = self.getGroup_name()
        return RBR(num_participant, group_name, random_block_size)

    ###minimization###
    ##!require object trial
    # return the index of
    def minimization_trial(self):
        """

        :return: allocation, group_scores
        """
        allocation, group_scores = MZ(self)
        self.setAllocation(allocation)
        self.updateGroupScore(group_scores)
        return allocation, group_scores

    # input a participant object
    # return the allocation group for that participant
    # and update the existed allocation
    def minimize_and_AddParticipant(self, participant):
        # check if there already exist an allocation
        assert self.__groupScore is not None
        group_id, group_name_alloc, group_scores_update = \
            MINI(participant.getCovarsIndex(), group_scores=self.__groupScore, group_names=self.group_name)
        self.updateGroupScore(group_scores_update)
        self.updateAllocation(alloc_name=group_name_alloc, participantId=participant.getID())
        return group_name_alloc

    def allocate_participant(self, participant, group_name_alloc):
        """
        allocate participant manually
        :return: allocation, group_scores
        """
        if self.__groupScore is None:  # init case
            self.__groupScore = {i: {j: len(self.factors.get(j)) * [0] for j in self.factors} for i in self.group_name}
            # initialize allocation(dictionary)
            self.allocation = {self.group_name[i]: [] for i in range(len(self.group_name))}
        # update group_scores
        participant_covarIndex = participant.getCovarsIndex()

        for key, value in participant_covarIndex.items():
            self.__groupScore[group_name_alloc][key][value] += 1

        self.updateAllocation(alloc_name=group_name_alloc, participantId=participant.getID())
        return self.allocation, self.__groupScore


class Strat_Trial:

    def __init__(self, trial_obj, covars):
        self.original_trial = trial_obj
        self.stratum = self.setStratum(covars)
        self.stratum_names = [str(key) for key in self.stratum]
        self.sub_trails = self.SetSubTrials()

    # split to sub-trails
    def setStratum(self, covars):
        # find all stratum for the new trial
        return stratify(self.original_trial, covars)

    def SetSubTrials(self):
        sub_trails = {}
        for key in self.stratum_names:
            IDs = self.stratum[key]
            sub_trails[key] = []
            # retrive participant info from IDs
            for id in IDs:
                id = int(id)
                par = self.original_trial.getParticipantByID(id)
                sub_trails[key].append(par)
        return sub_trails
