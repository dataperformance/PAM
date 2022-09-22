from .blockRand import block_randomization
import itertools as it


def strat_blcok_randomization(num_participant, group_name, block_size, covars):
    """
    The stratification block randomization
    :param int num_participant: the number of the participants
    :param list group_name: the list of allocation group names
    :param int block_size: the size of each block
    :param dictionary covars: e.g. {'sex': ["male","female"], "site": ["1","2"],"age_group": ["1","2","3"]}
    :return: the allocations for each stratum
    """

    assert block_size % len(group_name) == 0, "block size should be multiple of number of distinct group"
    assert num_participant % block_size == 0, "num_participant is multiple of block_size"

    num_stratum = 1  # init 1 stratum
    copy_covars = {}  # transform covars

    for var, level in covars.items():
        num_stratum = len(level) * num_stratum  # calculate the total number of stratum
        temp = []
        for i in level:
            temp.append((var, i))  # transform the list to list of pairs
        copy_covars[var] = temp

    assert num_participant % num_stratum == 0, "number_participant should be multiple of number of stratum"

    size_stratum = int(num_participant / num_stratum)  # the size of each stratum

    assigment = {}  # init the assigment for each stratum
    name_covars = covars.keys()

    list_stratum = list(it.product(*(copy_covars[name] for name in name_covars)))
    assigment = dict(zip(list_stratum, [[] for i in list_stratum]))  # init empty assigment

    for skey in assigment.keys():
        assigment[skey] = block_randomization(size_stratum, group_name,
                                              block_size)  # block randomization for each stratum

    return assigment

