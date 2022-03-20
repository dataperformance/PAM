from Alloc_Algorithm import Trial as Trial
from Alloc_Algorithm import Participant as Participant
from Alloc_Algorithm import Strat_Trial as Strat_Trial
import random as rd


'''     An setup example, assume we have the 500 participant, and they have 3 categorical variables, 
        SEX(male,female), SITE(1 or 2 ), AGE GROUP(1,2,3), and assign them into 5 different arms
'''


#setting the variables for the trial, i.e. name and levels for the trial
variables = {'sex': ["male","female"], "site": ["1","2"],"age_group": ["1","2","3"]}

#initilize the trial, which has the input of trial name, arm names for the trial, and the variables for the trial
group_names = ["A", "B", "C", "D", "E"]
trial_test = Trial("test", group_name=group_names, covars = variables)


"""Add 500 participants to the trial object:"""
print("generating random 500 participants")
for i in range(500):
    #randomly assigned the participant value, which is the index of the variables
    factor = [rd.randint(0,1), rd.randint(0,1), rd.randint(0,2)]
    #genearte one participant object, input participant ID, variables, and its index value
    p = Participant(ID=i,covars=variables, factor=factor)
    #add the participant to the trial we initialized at the beganing
    trial_test.addParticipant(p)

print("finish adding")


"""Simple Randomization, 2 options"""

#first option: static input
#input argument: number of participant, group names
#return argument: list of the assigned arms names
Trial.simple_rand(200,group_names)



#second option: simple randomization base on existed participants.
#input argument: the trial
#return argument: list of the assigned arms names
trial_test.simple_rand_participant()



"""block randomization, 2 options"""
#first option: static input
#input argument : number of participant, group names and block size
Trial.block_rand(200,group_names,block_size=5)

#second option: base on existed participants of a trial
#input argument : existed trail, group names and block size
trial_test.block_rand_participant(block_size=5)




"""Randomized block randomization, 2 options"""
random_block_size = [5,10,20]
#!!the number of participant need to be the common multiple of the random block size
#first option: generate the block randomization by providing the number of participant, group names, list of avaliable block sizes
Trial.rand_block_rand(300,group_names,random_block_size=random_block_size)

#second option: generate the randomization on the existed trial
trial_test.rand_block_rand_participant(random_block_size=random_block_size)




"""Minimization"""
#Do minimization on the existed trial
#return argument: list of the allocation of each individual participant ID for each arm
trial_test.minimization_trial()


#Add and allocation a new participant to the existed trail base on the minimization scheme
participant_new = Participant(ID=500, covars=variables, factor=[1,1,1])
trial_test.minimize_and_AddParticipant(participant_new)

#also, we can view the imbalance score for each arms.
trial_test.viewGroupScore()


#not finish
covars=["sex", "site", "age_group"]
t = Strat_Trial(trial_test,covars)


print()

