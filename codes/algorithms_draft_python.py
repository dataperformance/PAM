import pandas as pd
import random as rd
import sys


# authored by Dawei Yin


class Participant:
    def __init__(self, ID, covars, factor):
        self.ID = ID
        self.aloc = "Not Assigned"
        self.covar = {}
        #Initiate the paticipant covariables as a dictionary
        i = 0
        for key,value in covars.items():
            self.covar[key] = value[factor[i]]
            i +=1

        # input covars and stores it as factors, which is nested dictionary type with {variable:{level name: level index}}
        self.factors = {}
        for var, factors in covars.items():
            i = 0
            self.factors[var]= {}
            for level in factors:
                self.factors[var][level]= i
                i += 1

        # covarIndex is key/value pairs, key is the variable name, value is the index of the level.
        self.covarIndex = {}
        for key, value in self.factors.items():
            temp = self.covar[key]
            self.covarIndex[key] = self.factors[key][temp]

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
    def __init__(self, Trial_name, group_name, covars):
        self.Trial_name = Trial_name
        self.pars = []


        levels = []
        #the value of the trail dataframe
        vars = []
        for key, value in covars.items():
            levels.append(len(value))
            vars.append(key)

        # number of levels in each vars, stored in the list form
        self.leves = levels


        #self.df = pd.DataFrame(columns=['sex', 'site', 'age_group'])
        #dataframe of the trail
        self.df = pd.DataFrame(columns=vars)

        #self.factors = {"sex": {"male": 0, "female": 1}, "site": {"1": 0, "2": 1},
                        #"age_group": {"1": 0, "2": 1, "3": 2}}

        #input covars and stores it as factors, which is nested dictionary type with {variable:{level name: level index}}
        self.factors = {}
        for var, factors in covars.items():
            i = 0
            self.factors[var]= {}
            for level in factors:
                self.factors[var][level]= i
                i += 1



        # group_name  is the vector of string type, the name of study groups(check length of group_name>= 2 & equal to the length of ratio_group)
        self.group_name = group_name

    def getTrial_name(self):
        return self.Trial_name

    def setTrial_name(self, name):
        self.Trial_name = name

    def addParticipant(self, par):
        self.pars.append(par)
        par.covar["ID"] = int(par.getID())
        self.df = self.df.append(par.covar, ignore_index=True)

    def getParticipants(self):
        return self.pars

    def getParticipantID(self):
        return [i.getID() for i in self.pars]

    def getParticipantNum(self):
        return len(self.pars)

    def setGroup_name(self, group_name):
        self.group_name = group_name

    def getDataframe(self):
        return self.df

    def print_dataframe(self):
        return print(self.df)



    # Description: perform simple random allocation
    # Return arguments include seq(vector of group name, vector length equals to num_participant) and seed
    def simple_rand(self, seed=None, ratio_group=None):
        # num_participant is the int type, the number of study subject
        num_participant = self.getParticipantNum()
        # group_name  is the vector of string type, the name of study groups(check length of group_name>= 2 & equal to the length of ratio_group)
        group_name = self.group_name
        num_group = len(group_name)
        assert num_group >= 2

        # seed is random integer for the randomized function
        # if not assign seed, automatic assign seed to sys.maxsize
        if (seed == None):
            seed = rd.randrange(sys.maxsize)
            rd.Random(seed)
        rd.Random(seed)

        # ratio_group is a vector of the ratio, default ratio_group = vector(1/(num_group), length of num_group),
        # (check length of ratio_group >=2 & equal to the length of group_name & sum(ratio_group) ==1)
        if (ratio_group == None):
            ratio_group = [1 / num_group] * num_group
        assert len(ratio_group) >= 2, "length of ratio_group >=2"
        assert len(ratio_group) == num_group, "should equal to the length of group_name"
        assert sum(ratio_group) == 1, "sum(ratio_group) ==1"

        # Initialize the vector seq
        seq = []
        for i in range(num_participant):
            # assign the participant with the group
            # choose() is a built in function, return the str group name by randomly choose acocrding to its group ratio
            seq.append(rd.choices(group_name, ratio_group)[0])
        # return a tuple
        return seq, seed

    # Description: perform block random allocation
    # Return argument: seq (dimension x*y, x is the number of blocks, y is the block size, each row is the assignments of a block)
    def block_randomization(self, block_size):
        # group_name is the vector of string type, the name of study groups
        group_name = self.group_name
        # block_size is the int type, the number of participants in each block(check block_size >= 2 & block_size% length of group_name==0
        # , each block size>= 2 and is a multiple of number of group)
        assert block_size >= 2, "block size should larger than 2"
        assert block_size % len(group_name) == 0, "block size should be multiple of number of distinct group"

        # num_participant is the int type, the number of study subject (check num_participant %block_size ==0 & num_participant >0,
        # num_participant is multiple of block_size, and num_participant larger than 0)
        num_participant = self.getParticipantNum()
        assert num_participant % block_size == 0, "num_participant is multiple of block_size"
        assert num_participant > 0, "num_participant should larger than 0"

        # num_group is the number of distinct group()
        num_group = len(group_name)
        assert num_group >= 2, "group should more than 1"

        # number of blocks equal to the number of participant divides block_size, num_block is int type
        num_block = int(num_participant / block_size)

        # initialize the matrix seq(list in python)
        seq = []

        for i in range(num_block):
            seq.append(self.block_seq(num_group, block_size, group_name))

        return seq

    # Description: helper function to generate allocations within a block
    # Return argument is the assigned_block(the vector of group name, vector length equal to block_size)
    def block_seq(self, num_group, block_size, group_name):
        # int S, the number of occurrences of each distinctive groups
        S = int(block_size / num_group)

        # schedule_group is a copy of group_name S times in a vector
        schedule_group = group_name * S

        # initialize the vector assigned_block(list in python)
        assigned_block = []
        for i in range(block_size):
            # assign is the randomly selected element from the scheduler
            assign = rd.choice(schedule_group)
            # rd.choice is s a built-in function, return the randomly selected element of a vector

            # assign the group that randomly selected to the assigned_block
            assigned_block.append(assign)

            # remove the assigned block from the scheduler
            schedule_group.remove(assign)
            # remove() is a built-in function, removed elements of a vector
        return assigned_block

    # Description: block randomization with randomized block size,variation of block randomization
    # Return argument: seq (dimension x*y, x is the number of blocks, y is the random block size, each row is the assignments of a block)

    def randomized_block_randomization(self, random_block_size):
        # num_participant is the int type, the number of study subject (check num_participant % each element of random_block_size ==0 & num_participant >0,
        # num_participant is multiple of each element of random_block_size, and num_participant larger than 0)
        num_participant = self.getParticipantNum()
        assert num_participant > 0, "num_participant should larger than 0"
        # random_block_size is a vector of int type, the provided block sizes that can be chose from to perform the randomized block randomization
        # (check each int element in random_block_size is a multiple of num_group)
        for n in random_block_size:
            assert n > 1, "random block size should larger than 1"
            assert num_participant % n == 0, "num_participant should be multiple of each element of random_block_size"

        # group_name is the vector of string type, the name of study groups (check length of group_name>= 2)
        group_name = self.group_name
        assert len(group_name) >= 2, "length of group_name should larger than 2"

        # num_group is the number of distinct group()
        num_group = len(group_name)
        assert num_group >= 2, "group should more than 1"

        # make a copy of num_participant
        num_remaining_participant = num_participant

        # initialize the vector of vectors seq(list in python)
        seq = []



        # loop until Num_Remaining_participant is larger than 0
        while num_remaining_participant > 0:
            # if Num_Remaining_participant is equal to smallest element of random_block_size,
            # assigned the last block_size as the Num_Remaining_participant
            if num_remaining_participant == min(random_block_size):
                block_size = num_remaining_participant
                # seq append the vector of string with length of block_size
                seq.append(self.block_seq(num_group, block_size, group_name))
                break
            #else,
            else:
                # block_size is randomly choose from random_block_size
                block_size = rd.choice(random_block_size)
                # rd.choice() is a built-in function, return the randomly selected element of a vector

                # seq append the vector of string with length of block_size
                seq.append(self.block_seq(num_group, block_size, group_name))

                #update number of remaining participant that needs to be assigned
                num_remaining_participant = num_remaining_participant - block_size


        return seq

    # Description: perform minimization allocation
    # Return arguments includes allocations(vectors of group allocation for each group, element of the vectors is the participant ID number), group_scores(nested key/value pair to represent the imbalance scores)

    def minimization(self):

        # group_name is a list,
        # the name of study groups(check length of group_name>= 2 & equal to the length of ratio_group)
        group_names = self.group_name
        # num_group is the unique number of the study groups
        num_group = len(group_names)
        # group_scores is nested key/value pair with two layers, first layer’s key is the group_names, and the value is the covariables of the group;
        # the second layer’s key is the covariable names, and its value is vector of int, which store the scores.
        group_scores = {i: {j: len(self.factors.get(j)) * [0] for j in self.factors} for i in self.group_name}
        #group_scores = pd.DataFrame(group_scores)  # better visulization


        #intialize allocation
        allocation = [[] for i in range(num_group)]

        #
        collection_participants = self.getParticipants()

        #
        first_participant = collection_participants[0]
        # updata collection_participants
        collection_participants = collection_participants[1:]

        # first case, randomly allocate first participant
        group_id = rd.randint(0, num_group - 1)

        # group_name is the name of the group that assigned to first participant
        group_name = group_names[group_id]

        # updata allocation
        allocation[group_id].append(first_participant.getID())
        # first_participant.setAloc(group_name)

        # updata group_scores
        first_participant_covarIndex = first_participant.getCovarsIndex()
        for key, value in first_participant_covarIndex.items():
            group_scores[group_name][key][value] += 1

        # allocate the rest participants
        for i in range(len(collection_participants)):
            # extract the participant
            participant = collection_participants[i]
            # call the minimize function to
            group_id, group_name_assigned, group_scores_update = \
                minimize(participant.getCovarsIndex(), group_scores, group_names)
            # updata group_scores by re-reference the group_socres
            group_scores = group_scores_update

            #
            allocation[group_id].append(participant.getID())

        return allocation, group_scores



    # Description: stratify the trail subjects into strutms
    # Input argument: the list of string of the variable names that are used to stratify the dataframe
    # Return_argument: individual statums

    def stratify(self, covars):
        #check if covars in the actual dataframe
        self_var_name = [i for i in self.factors.keys().__iter__()]
        for v in covars:
            assert v in self_var_name

        result= []
        grouped_df = self.df.groupby(covars)
        for key, item in grouped_df:
            result.append(grouped_df.get_group(key))
        return result
# Decription:helper function for allocate a single participant according to the group_scores
# Return arguments: the group_id, group_name_alloc, group_scores for allocating a participant by the minimization algorithm.

def minimize(Participant_covarsIndex, group_scores, group_names):
    scores_total = []

    group_scores_update = group_scores.copy()
    # for each group, calculate the mariginal socres
    for group_name in group_scores_update:
        # locate group_name index
        group_name_index = group_names.index(group_name)
        score = 0
        # find marginal scores for each group
        for key, value in Participant_covarsIndex.items():
            # find imbalance score for if assigned
            score = score + group_scores_update[group_name][key][value] + 1

        scores_total.append(score)

    # print(scores_total)

    # return min group imbalance index
    min_imbalance = min(scores_total)
    # retrun all min_groups' index
    min_groups_index = [i for i, x in enumerate(scores_total) if x == min_imbalance]
    # randomly choose a min imbalance group if multiple min imbalance, otherwise return min
    group_id = rd.choice(min_groups_index)  # break tier when multiple min occur
    # update the allocate group name
    group_name_alloc = group_names[group_id]

    # updata scores
    # group_scores = group_scores[group_id]
    for key, value in Participant_covarsIndex.items():
        group_scores_update[group_name_alloc][key][value] += 1

    return group_id, group_name_alloc, group_scores_update


# simple illustration

#participant needs: ID, covars(dictionaty), value(list)









covars = {'sex': ["male","female"], "site": ["1","2"],"age_group": ["1","2","3"]}#, "Test1": ["T", "F"]}
x = Trial("test", group_name=["A", "B", "C", "D", "E"], covars = covars)

#par1 = Participant(ID=1,covars= covars, factor = [0,1,1])
#par2 = Participant(ID=2,covars= covars, factor = [1,1,1])
#par3 = Participant(ID=3,covars= covars, factor = [0,0,0])
#par4 = Participant(ID=4,covars= covars, factor = [0,1,2])
#par5 = Participant(ID=5,covars= covars, factor = [0,0,1])
#par6 = Participant(ID=6,covars= covars, factor = [1,0,2])
#par7 = Participant(ID=3,covars= covars, factor = [0,0,0,0])
#par8 = Participant(ID=4,covars= covars, factor = [0,0,0,1])
#par9 = Participant(ID=4,covars= covars, factor = [0,0,0,1])


#x.addParticipant(par1)
#x.addParticipant(par2)
#x.addParticipant(par3)
#x.addParticipant(par4)
#x.addParticipant(par5)
#x.addParticipant(par6)
#x.addParticipant(par7)
#x.addParticipant(par8)
#x.addParticipant(par9)



#test 500 participants:
print("generating random test case")
for i in range(500):
    factor = [rd.randint(0,1), rd.randint(0,1), rd.randint(0,2)]
    p = Participant(ID=i,covars=covars, factor=factor)
    x.addParticipant(p)
print("finish adding")


#print(x.simple_rand())
#print("block randomization: ", x.block_randomization(5))
#print("randomized block randomization: ", x.randomized_block_randomization([3, 3]))
allocation, scores = x.minimization()
#print("minimization allocation: ", allocation)

#print(scores)




test = x.stratify(covars=["sex", "site", "age_group"])






print("end")
