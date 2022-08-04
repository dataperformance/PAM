import random as rd
import sys

####Simple Randomization:####
# The algorithm is from < (Lin, Zhu, & Su, 2015)>
# Description: perform simple random allocation
# Return arguments include seq(vector of group name, vector length equals to num_participant) and seed

def simple_rand(num_participant,group_name, seed=None, ratio_group=None):
    # num_participant is the int type, the number of study subject
    # group_name  is the vector of string type,
    #the name of study groups(check length of group_name>= 2 & equal to the length of ratio_group)
    #num_group is the int type,
    #equal to the number of distinctive groups
    num_group = len(group_name)
    assert num_group >= 2  # number of groups should larger than 2

    # seed is random integer for the randomized function
    # if not assign seed, automatic assign seed to sys.maxsize
    if (seed == None):
        seed = rd.randrange(sys.maxsize)
        rd.Random(seed)
    # if seed is assigned, set seed to the assigned value
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
