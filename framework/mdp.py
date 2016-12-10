import collections
import random
import math

class RLAlgorithm:
    # Produce an action given a state.
    def getAction(self, state): raise NotImplementedError("Override me")

    # If |state| is a terminal state, this function will be called with (s, a,
    # 0, None). When this function is called, it indicates that taking action |action|
    # in state |state| resulted in reward |reward| and a transition to state |newState|.
    def incorporateFeedback(self, state, action, reward, newState): raise NotImplementedError("Override me")



class QLearningAlgorithm(RLAlgorithm):
    def __init__(self, possible_actions, discount, featureExtractor, explorationProb=0.2):
        self.possible_actions = possible_actions
        self.discount = discount
        self.featureExtractor = featureExtractor
        self.explorationProb = explorationProb
        self.weights = collections.defaultdict(float)
        self.numIters = 0

    # Return the Q function associated with the weights and features
    def getQ(self, state, action):
        score = 0
        for f, v in self.featureExtractor(state, action):
            score += self.weights[f] * v
        return score

    # This algorithm will produce an action given a state.
    # Here we use the epsilon-greedy algorithm: with probability
    # |explorationProb|, take a random action.
    def getAction(self, state):
        state_actions = self.possible_actions(state)
        self.numIters += 1
        if random.random() < self.explorationProb:
            return random.choice(state_actions)
        else:
            return max((self.getQ(state, action), action) for action in state_actions)[1]

    # Call this function to get the step size to update the weights.
    def getStepSize(self):
        return 1.0 / math.sqrt(self.numIters)

    # We will call this function with (s, a, r, s'), which you should use to update |weights|.
    # Note that if s is a terminal state, then s' will be None.  Remember to check for this.
    # You should update the weights using self.getStepSize(); use
    # self.getQ() to compute the current estimate of the parameters.
    def incorporateFeedback(self, state, action, reward, newState):
        if (newState == None): pass
        Vopt = max([self.getQ(newState, a) for a in self.possible_actions(newState)])
        getQ = self.getQ(state, action)
        for f, v in self.featureExtractor(state, action):
            self.weights[f] -= self.getStepSize() * (getQ - (reward + self.discount * Vopt)) * v


