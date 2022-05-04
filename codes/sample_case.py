from Alloc_Algorithm import Trial as Trial
from Alloc_Algorithm import Participant as Participant
from Alloc_Algorithm import Strat_Trial as Strat_Trial
import random as rd
import timeit
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


'''     An example, assume we have the 500 participant, and they have 3 categorical variables, 
        SEX(male,female), SITE(1 or 2 ), AGE GROUP(1,2,3), and assign them into 5 different arms
'''


#setting the variables for the trial, i.e. name and levels for the trial
variables = {'sex': ["male","female"], "site": ["1","2"],"age_group": ["1","2","3"]}

#initilize the trial, which has the input of trial name, arm names for the trial, and the variables for the trial
group_names = ["A", "B", "C", "D", "E"]

Trial_test_500 = Trial("test", group_name=group_names, covars = variables)


"""Add 500 participants to the trial object:"""
start = timeit.default_timer()
print("generating random 500 participants")
for i in range(500):
    #randomly assigned the participant value, which is the index of the variables
    covarIndex = {
        'sex': rd.randint(0,1),
        "site": rd.randint(0,1),
        "age_group":rd.randint(0,1)
    }

    #genearte one participant object, input participant ID, variables, and its index value
    p = Participant(ID=i,covars=variables, covarIndex=covarIndex)
    #add the participant to the trial we initialized at the beganing
    Trial_test_500.addParticipant(p)
print("finish adding")
elapsed = (timeit.default_timer() - start)
print("The total time for adding 500 participants is: ", round(elapsed,5), "seconds")

"""Simple Randomization, 2 options"""

#first option: static input
#input argument: number of participant, group names
#return argument: list of the assigned arms names
start = timeit.default_timer()
Trial.simple_rand(500,group_names)
elapsed = (timeit.default_timer() - start)
print("The total time for simple randomization(1) 500 participants is: ", round(elapsed,5), "seconds")


#second option: simple randomization base on existed participants.
#input argument: the trial
#return argument: list of the assigned arms names
start = timeit.default_timer()
Trial_test_500.simple_rand_participant()
elapsed = (timeit.default_timer() - start)
print("The total time for simple randomization(2) 500 participants is: ", round(elapsed,5), "seconds")


"""block randomization, 2 options"""
#first option: static input
#input argument : number of participant, group names and block size
start = timeit.default_timer()
Trial.block_rand(500,group_names,block_size=5)
elapsed = (timeit.default_timer() - start)
print("The total time for block randomization(1) 500 participants with block size 5 is: ", round(elapsed,5), "seconds")


#second option: base on existed participants of a trial
#input argument : existed trail, group names and block size
start = timeit.default_timer()
Trial_test_500.block_rand_participant(block_size=5)
elapsed = (timeit.default_timer() - start)
print("The total time for block randomization(2) 500 participants with block size 5 is: ", round(elapsed,5), "seconds")



"""Randomized block randomization, 2 options"""
start = timeit.default_timer()
random_block_size = [5,10,20]
#!!the number of participant need to be the common multiple of the random block size
#first option: generate the block randomization by providing the number of participant, group names, list of avaliable block sizes
Trial.rand_block_rand(500,group_names,random_block_size=random_block_size)
elapsed = (timeit.default_timer() - start)
print("The total time for randomized block randomization(1) 500 participants with block size 5,10,20 is: ", round(elapsed,5), "seconds")



#second option: generate the randomization on the existed trial
start = timeit.default_timer()
Trial_test_500.rand_block_rand_participant(random_block_size=random_block_size)
elapsed = (timeit.default_timer() - start)
print("The total time for randomized block randomization(2) 500 participants with block size 5,10,20 is: ", round(elapsed,5), "seconds")




"""Minimization"""
#Do minimization on the existed trial
#return argument: list of the allocation of each individual participant ID for each arm
start = timeit.default_timer()
Trial_test_500.minimization_trial()
elapsed = (timeit.default_timer() - start)
print("The total time for Minimization 500 participants is: ", round(elapsed,5), "seconds")

#Add and allocation a new participant to the existed trail base on the minimization scheme
start = timeit.default_timer()
covarIndex = {
        'sex': 1,
        "site": 1,
        "age_group":1
    }
participant_new = Participant(ID=500, covars=variables, covarIndex=covarIndex)
Trial_test_500.minimize_and_AddParticipant(participant_new)
elapsed = (timeit.default_timer() - start)
print("The time for Minimize a participant is: ", round(elapsed,5), "seconds")
#also, we can view the imbalance score for each arms.
Trial_test_500.viewGroupScore()


#not finish
covars=["sex", "site", "age_group"]
t = Strat_Trial(Trial_test_500,covars)
print("end example")




"""Time test"""
'''Test time for '''

Trial_test_time = Trial("test_time", group_name=group_names, covars = variables)


nums_participant = [100,500,1000,5000,10000,50000]
#records of times for each method
time_AddParticipant = []
time_SimpleRand = []
time_BlockRand = []
time_RandBlockRand = []
time_Minimization =[]


for num in nums_participant:
    print("generating",num,"participants ...")
    start = timeit.default_timer()
    for i in range(num):
        #randomly assigned the participant value, which is the index of the variables
        covarIndex = {
            'sex': rd.randint(0, 1),
            "site": rd.randint(0, 1),
            "age_group": rd.randint(0, 2)
        }
        #genearte one participant object, input participant ID, variables, and its index value
        p = Participant(ID=i,covars=variables, covarIndex=covarIndex)
        #add the participant to the trial we initialized at the beganing
        Trial_test_time.addParticipant(p)
    print("Done generating")
    #record time for adding the participant
    elapsed_1 = (timeit.default_timer() - start)
    time_AddParticipant.append(elapsed_1)

    #time test for simple rand
    start = timeit.default_timer()
    Trial_test_time.simple_rand_participant()
    elapsed_2 = (timeit.default_timer() - start)
    time_SimpleRand.append(elapsed_2)

    #time test for block rand
    start = timeit.default_timer()
    Trial_test_time.block_rand_participant(block_size=5)
    elapsed_3 = (timeit.default_timer() - start)
    time_BlockRand.append(elapsed_3)

    #time test for randomized block rand
    start = timeit.default_timer()
    Trial_test_time.rand_block_rand_participant(random_block_size=random_block_size)
    elapsed_4 = (timeit.default_timer() - start)
    time_RandBlockRand.append(elapsed_4)

    # time test for minimization
    start = timeit.default_timer()
    Trial_test_time.minimization_trial()
    elapsed_5 = (timeit.default_timer() - start)
    time_Minimization.append(elapsed_5)

    print(num, " participant generating time: ", elapsed_1)
    print("Simple randomization time: ", elapsed_2)
    print("Block randomization time: ", elapsed_3)
    print("Rand block randomization time: ", elapsed_4)
    print("Minimization time: ", elapsed_5)

"""show the time result"""
import matplotlib.pyplot as plt

#generating time:
plt.plot(nums_participant,time_AddParticipant)
plt.title("Time for adding participants")
plt.xlabel("number of participants")
plt.ylabel("time in seconds")
plt.show()


#simple rand time:
plt.plot(nums_participant,time_SimpleRand)
plt.title("Time of simple randomization ")
plt.xlabel("number of participants")
plt.ylabel("time in seconds")
plt.show()

#block rand time:
plt.plot(nums_participant,time_BlockRand)
plt.title("Time of block randomization")
plt.xlabel("number of participants")
plt.ylabel("time in seconds")
plt.show()



#rand block rand time:
plt.plot(nums_participant,time_RandBlockRand)
plt.title("Time of randomized block randomization")
plt.xlabel("number of participants")
plt.ylabel("time in seconds")
plt.show()

#rand block rand time:
plt.plot(nums_participant,time_Minimization)
plt.title("Time of minimization")
plt.xlabel("number of participants")
plt.ylabel("time in seconds")
plt.show()


print()

