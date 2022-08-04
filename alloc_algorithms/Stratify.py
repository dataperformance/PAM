import pandas as pd

###Stratification###

""" Description: stratify all the participant into stratum by covariables
    Input argument: the list of string of the variable names that are used to stratify the dataframe
    Return_argument: list of individual stratum, which each element of the list is a pandas Dataframe
"""
def stratify(self, covars):
    #check if covars in the actual dataset
    self_var_name = [i for i in self.factors.keys().__iter__()]
    for v in covars:
        assert v in self_var_name
    #initilize the result
    result = {}
    #use pandas to stratify by each variable in all covariables
    grouped_df = self.df.groupby(covars)

    for key, item in grouped_df:
        stratum = grouped_df.get_group(key)
        IDs = stratum['ID']
        stratum_name = str(grouped_df.get_group(key).iloc[1, :-1].values)
        result[stratum_name] = IDs

    return result
