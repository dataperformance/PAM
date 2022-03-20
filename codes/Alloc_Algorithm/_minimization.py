import random as rd

####Minimization:####
''' The algorithm is from < (Lim & In, 2005), (Scott, McPherson, Ramsay, & Campbell, 2002)>
    Description: perform minimization allocation
    Return arguments includes allocations(vectors of group allocation for each group,
    -element of the vectors is the participant ID number), group_scores(nested key/value pair to represent the imbalance scores)
'''

def minimization(self):

    # group_name is a list,
    # the name of study groups(check length of group_name>= 2 & equal to the length of ratio_group)
    group_names = self.group_name

    # num_group is the unique number of the study groups
    num_group = len(group_names)

    # group_scores is nested key/value pair with two layers,
    # first layer’s key is the group_names, and the value is the covariables of the group;
    # the second layer’s key is the covariable names, and its value is vector of int, which store the scores.
    group_scores = {i: {j: len(self.factors.get(j)) * [0] for j in self.factors} for i in self.group_name}

    #group_scores = pd.DataFrame(group_scores)  # better visulization


    # intialize allocation
    allocation = [[] for i in range(num_group)]

    # collection_participants is a list of the participant in the trail
    collection_participants = self.getParticipants()


    # first_participant is the first paticipant to be allocated
    first_participant = collection_participants[0]

    # update collection_participants
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
        # update group_scores by re-reference the group_socres
        group_scores = group_scores_update

        # update the allocation result
        allocation[group_id].append(participant.getID())

    return allocation, group_scores



''' Description: helper function for allocating a single participant according to the group_scores,
    Return arguments: the group_id, group_name_alloc, group_scores for allocating a participant by the minimization algorithm.
'''
def minimize(Participant_covarsIndex, group_scores, group_names):

    #initilize the scores_total,
    #scores_total is a list int,
    # which each element is the imbalance scores of that group
    scores_total = []

    #make a deep copy of previous group scores
    group_scores_update = group_scores.copy()

    # for each group, calculate the marginal scores(for each group)
    for group_name in group_scores_update:
        # locate group_name index
        group_name_index = group_names.index(group_name)
        score = 0
        # find marginal scores for each group
        for key, value in Participant_covarsIndex.items():
            # find imbalance score for if assigned
            score = score + group_scores_update[group_name][key][value] + 1
        #update the scores_total
        scores_total.append(score)

    # return min group imbalance index
    min_imbalance = min(scores_total)
    # return all min_groups' index
    min_groups_index = [i for i, x in enumerate(scores_total) if x == min_imbalance]
    # randomly choose a min imbalance group if multiple min imbalance, otherwise return min
    group_id = rd.choice(min_groups_index)  # break tier when multiple min occur
    # update the allocate group name
    group_name_alloc = group_names[group_id]

    # update scores and return
    for key, value in Participant_covarsIndex.items():
        group_scores_update[group_name_alloc][key][value] += 1

    return group_id, group_name_alloc, group_scores_update
