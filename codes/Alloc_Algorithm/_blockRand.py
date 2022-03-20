import random as rd

####Block Randomization:####

""" The algorithm is from < (Broglio, 2018), (Lim & In, 2005)>
    Description: perform block random allocation
    Return argument: seq (dimension x*y, x is the number of blocks, y is the block size, each row is the assignments of a block)
"""
def block_randomization(num_participant, group_name, block_size):

    # group_name is the vector of string type, the name of study groups
    # block_size is the int type, the number of participants in each block(check block_size >= 2 & block_size% length of group_name==0
    # , each block size>= 2 and is a multiple of number of group)
    assert block_size >= 2, "block size should larger than 2"
    assert block_size % len(group_name) == 0, "block size should be multiple of number of distinct group"

    # num_participant is the int type, the number of study subject (check num_participant %block_size ==0 & num_participant >0,
    # num_participant is multiple of block_size, and num_participant larger than 0)
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
        seq.append(block_seq(num_group, block_size, group_name))

    return seq


""" Description: helper function to generate allocations within a block
    Return argument is the assigned_block(the vector of group name, vector length equal to block_size)
"""
def block_seq(num_group, block_size, group_name):
    # int S, the number of occurrences of each distinctive groups
    S = int(block_size / num_group)

    # schedule_group is a copy of group_name S times in a vector
    schedule_group = group_name * S

    # initialize the vector assigned_block(list in python)
    assigned_block = []

    #For each element in the block, assign group
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



""" The algorithm is from < (Lim & In, 2005)>
    Description: block randomization with randomized block size,variation of block randomization
    Return argument: seq (dimension x*y, x is the number of blocks, y is the random block size, each row is the assignments of a block)
"""
def randomized_block_randomization(num_participant,group_name,random_block_size):
    # num_participant is the int type, the number of study subject (check num_participant % each element of random_block_size ==0 & num_participant >0,
    # num_participant is multiple of each element of random_block_size, and num_participant larger than 0)

    assert num_participant > 0, "num_participant should larger than 0"
    # random_block_size is a vector of int type, the provided block sizes that can be chose from to perform the randomized block randomization
    # (check each int element in random_block_size is a multiple of num_group)
    for n in random_block_size:
        assert n > 1, "random block size should larger than 1"
        assert num_participant % n == 0, "num_participant should be multiple of each element of random_block_size"

    # group_name is the vector of string type, the name of study groups (check length of group_name>= 2)
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
            seq.append(block_seq(num_group, block_size, group_name))
            break
        #else
        else:
            # block_size is randomly choose from random_block_size
            block_size = rd.choice(random_block_size)
            # rd.choice() is a built-in function, return the randomly selected element of a vector

            # seq append the vector of string with length of block_size
            seq.append(block_seq(num_group, block_size, group_name))

            #update number of remaining participant that needs to be assigned
            num_remaining_participant = num_remaining_participant - block_size

    return seq

