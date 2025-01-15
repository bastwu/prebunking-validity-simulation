import random as rand
from collections import Counter

class Agent:
    """
    Initializes an agent with
    opinion        1, 2, or 3 (no opinion, disinformation, fact-checkers)
    status         "S", "I", "uI", "R" or "aR" (susceptible, infected, resistant)
    share          True or False (can the node actively shares information?)
    frequency      (int) (how much is shared per share call)
    resistance     True or False (is the node able to change its opinion?)
    dark           True or False (is the node a dark agent?)

    that can believe and/or share their opinion
    and can output their network information
    """

    def __init__(self, prob_prebunk, node_id, prob_share_opinion, prob_immune, opinion=0, status="S", frequency=1, resistance=False, dark=False):
        """
        [default]
        opinion: (int)
            [0]: no opinion
            1: disinformation
            2: fact checking
        status: (str)
            ["S"]: susceptible
            "I": infected
            "R": resistant
        prob_share_opinion: (float)
            probability to share a node's opinion with its neighbour
        frequency: (int)
            [1]: how often the opinion is shared per share call
        resistance: (bool)
            True: can't change their opinion
            [False]: can change their opinion
        dark: (bool)
            True: is a 'dark agent' that can trigger disinformation campaigns
            [False]: not a dark agent
        """
        self.prob_prebunk = prob_prebunk
        self.opinion = opinion
        self.status = status
        self.prob_share_opinion = prob_share_opinion
        self.frequency = frequency
        self.resistance = resistance

        self.dark = dark
        self.active_attack = False
        self.pause = False
        self.attack_frequency = 50

        self.prob_disinfo = .5 # probability to become a disinformation agent
        #self.prob_prebunk = 1 # probability to become a prebunking agent
        self.prob_immune = prob_immune # probability to become immunized against disinformation

        self.friends = []
        self.node_id = node_id

        self.opinion_history = []
        self.engagement = []
        self.next_opinion = False

    def share(self):
        """
        Defines the sharing behavior of nodes: Either has no opinion, shares disinformation, or fact checking information
        """
        self.engagement = []

        if rand.random() <= self.prob_share_opinion:
            if self.opinion == 0:
                # no opinion
                self.engagement = [0 for _ in range(self.frequency)]
            elif self.opinion == 2:
                # Fact checking
                self.engagement = [2 for _ in range(self.frequency)]
            elif self.opinion == 1:
                # Disinformation
                self.engagement = [1 for _ in range(self.frequency)]
            else:
                raise ValueError

    def check_friends(self):
        """
        Based on the neighbouring nodes, the status of the node under consideration is updated
        """
        if self.resistance:
            self.next_opinion = self.opinion  # If resistant, nothing changes
            return

        # Get all opinion from friends
        all_opinions = []
        for friend in self.friends:
            all_opinions.extend(friend.engagement)
        count = Counter(all_opinions)

        # Handle disinformation logic (opinion 1)
        n_1 = count.get(1)
        if n_1:
            prob = n_1 / len(all_opinions)
            if prob > self.prob_disinfo:
                self.next_opinion = 1  # Disinformation
                self.status = "I"  # Infected
                self.resistance = True
                return

        # Handle fact-checking logic (opinion 2)
        n_2 = count.get(2)
        if n_2:
            if rand.random() < self.prob_prebunk:  # Will an Agent be immunised?
                self.resistance = True
                self.status = "R"
                self.next_opinion = 0

                if rand.random() < self.prob_immune:  # Will an Agent be immunised AND shares prebunking content?
                    self.next_opinion = 2
                    self.status = 'aR'
                return

        self.next_opinion = self.opinion

    def update_opinion(self):
        """
        Records and changes the opinion of the node (from no opinion to either infected or resistant)
        """
        self.opinion_history.append(self.opinion)
        self.opinion = self.next_opinion

    def node_output(self):
        """
        Status of the node that can be requested.
        """
        return (
            self.node_id,
            dict(
                opinion=self.opinion,
                status=self.status,
                share=self.share,
                resistance=self.resistance,
                dark=self.dark,
            )
        )

    def tie_output(self):
        """
        List of neighbouring friends of a node that can be requested.
        """
        tie_list = []
        for friend in self.friends:
            tie_list.append((
                self.node_id,
                friend.node_id
            ))

        return tie_list

    def attack(self, tick, kind, start):

        """
        Executes an attack based on the given attack type (kind) and simulation step (tick), starting at given
        simulation step (start).
        """
    #if self.dark:
        match kind:
            case 0: # Scenario 1: One single step with 50 times sharing
                if tick == start:
                    self.frequency = 50
                    self.share()
                    self.frequency = 1
                    return
                self.share()
            case 1: # Scenario 2: With an increasing volume(10, 30, and 50 times) over three steps with a step of
                    # normal sharing behavior in between the attack steps
                if tick == start:
                    self.frequency = 10
                    self.share()
                    self.frequency = 1
                elif tick == start + 2:
                    self.frequency = 30
                    self.share()
                    self.frequency = 1
                elif tick == start + 4:
                    self.frequency = 50
                    self.share()
                    self.frequency = 1
                else:
                    self.share()
            case 2: # Scenario 3: Frequency decreases over 5 steps, each step 2 ticks long (50, 40 ,30, 20, 10) Times
                frequency_values = [50, 50, 40, 40, 30, 30, 20, 20, 10, 10]
                if tick < len(frequency_values) + start:
                    actual_value = frequency_values[tick - start]
                    self.frequency = actual_value
                else:
                    self.frequency = 1

                self.share()
            case _: # Default behaviour
                self.share()

    def alter_agent(self, kind):
        """
        Change the status of the agent
        kind: (str)
            ['dark']: dark agent type
            'light': fact-checking sharing agent
        attack_strength: (int)
            [50]: intensity of the attack
        """
        if kind == 'dark':
            self.opinion = 1
            self.status = 'uI'
            self.prob_share_opinion = 1
            self.frequency = 1
            self.resistance = True
            self.dark = True

        elif kind == 'light':
            self.opinion = 2
            self.status = 'aR'
            self.prob_share_opinion = 1
            self.frequency = 1
            self.resistance = True
            self.dark = False
