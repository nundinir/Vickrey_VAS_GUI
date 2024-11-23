import numpy as np

class robobidder():
    """
    Simulated Vickrey Auction Bidder using 1st order exponential value function
    """
    def __init__(self, k, b):
        # Robovalue Parameters
        self.k = k
        self.b = b

        # State Variables
        self.newest_walk_start = 0
        self.newest_walk_end = 0

        # Perturbing initial k bid (representing noise in initial biding)
        self.robovalue = self.k + np.random.normal(loc = 0, scale = 0.01) 

    def walk(self, walk_end_time, walk_start_time):
        """
        Update robovalue and state variables
        """
        self.robovalue = self.k*np.exp(self.b*(walk_end_time - walk_start_time))
        self.newest_walk_start = walk_start_time
        self.newest_walk_end = walk_end_time

    def getstate(self):
        """
        Return state variables
        """
        return self.newest_walk_end, self.newest_walk_start
    
    def loadstate(self, newest_walk_end, newest_walk_start):
        """
        Set state variables and walk
        """
        self.newest_walk_start = newest_walk_start
        self.newest_walk_end = newest_walk_end
        self.walk(self.newest_walk_end, self.newest_walk_start)

    def robobid(self):
        """
        Return robovalue with added Gaussian noise
        """
        return round(self.robovalue + np.random.normal(loc = 0, scale=0.01), 2)

class roboModel():
    """
    Collection of robobidders
    """
    def __init__(self, k, b, num_robobidders): 
        # Robovalue Parameters
        self.k = k
        self.b = b

        # Create robobidders
        self.robobidderlist = [robobidder(k, b) for _ in range(num_robobidders)]

    def get_bids(self):
        """
        Return list of robobids
        """
        return [rb.robobid() for rb in self.robobidderlist]

    def name(self):
        """
        Return robomodel information
        """
        modelName = "k: {:.4f}, b: {:.4f}, number of robobidders: {}"
        return modelName.format(self.k, self.b, len(self.robobidderlist))
    
    def getstate(self):
        """
        Returns list of robobidder state variables 
        """
        robostates = []
        for robo in self.robobidderlist:
            robostates.extend(robo.getstate())
        return robostates
    
    def loadstate(self, statelist: list):
        """
        Load states into robobidders
        """
        try:
            assert(len(statelist)/2 == len(self.robobidderlist))
        except:
            Exception("Robobidder load failed: Unequal states to robobidders")

        for robo in self.robobidderlist:
            walk_end = int(statelist.pop(0))
            walk_start = int(statelist.pop(0))
            robo.loadstate(walk_end, walk_start)


if __name__ == "__main__":
    # Robobidder State Demo
    from constants import k_RB, b_RB
    robomodel = roboModel(k_RB, b_RB, 2)

    # Print robobidder states walk_end, walk_start in ascending robobidder order
    print("Initial State: ", robomodel.getstate())

    # Walk robo1 for 0-10 minutes
    robomodel.robobidderlist[0].walk(20, 0)
    print("Walk robobidder 0, ", robomodel.getstate())

    print("Bids 0, 1: ", robomodel.robobidderlist[0].robobid(), robomodel.robobidderlist[1].robobid())

    # Load statelist into robomodel
    statelist = [130, 22, 44, 0]
    print("State to load: ", statelist)
    robomodel.loadstate(statelist)

    print("Robomodel state: ", robomodel.getstate())
    print("Robomodel bids: ", robomodel.get_bids())

    print("End of Demo")
