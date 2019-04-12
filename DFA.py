class State:
    def __init__(self, accepted, jmps):
        self.accepted = accepted
        self.jmps = jmps

    def step(self, x):
        if x in self.jmps:
            return True, self.jmps[x]
        elif self.accepted == False:
            raise Exception('Error in executing automator when handling '+x)
        else:
            return False, None

class DFA:
    def __init__(self, states_acc, states_jmps):
        '''
        :param
        states_acc: a list of boolean values e.g. [True, False, ...]
        states_jmps: a list of information for initiating each state in automator
        e.g. [{'a1': 3, 'a2': 5, 'a3': 2}, {...}]
        '''
        self.string = '' # the input which has been matched
        self.states = []
        for i, jmps in enumerate(states_jmps):
            acc = states_acc[i]
            self.states.append(State(acc, jmps))
        self.curState = self.states[0]

    def reset(self):
        self.string = ''
        self.curState = self.states[0]

    def execute(self, src_code, i, code):
        while i < len(src_code):
            x = src_code[i]
            valid, nxtStateIdx = self.curState.step(x)
            nxtState = self.states[nxtStateIdx]
            if valid == True:
                self.curState = nxtState
                self.string += x
            else:
                res = code[self.string] if self.string in ["int", "float", "bool",
                                                           "struct", "if", "else",
                                                           "do", "while"] else code["id"]\
                    , self.string, i
                self.reset()
                return res
            i += 1

