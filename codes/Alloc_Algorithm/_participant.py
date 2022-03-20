


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