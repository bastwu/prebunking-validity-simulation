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

    def __init__(self, opinion=0, status="S", shares=.5, frequency=1, resistance=False, dark=False):
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
        share: (bool)
            [True]: can share their opinion
            False: can't share their opinion
        frequency: (int)
            [1]: how often the opinion is shared per share call
        resistance: (bool)
            True: can't change their opinion
            [False]: can change their opinion
        dark: (bool)
            True: is a 'dark agent' that can trigger disinformation campaigns
            [False]: not a dark agent
        """
        self.opinion = opinion
        self.status = status
        self.shares = shares
        self.frequency = frequency
        self.resistance = resistance

        self.dark = dark
        self.active_attack = False
        self.pause = False
        self.attack_frequency = 50

        self.prop_1 = .5
        self.prop_2 = 1
        self.prop_vax = 0

        self.friends = []
        self.node_id = None

        self.opinion_history = []
        self.engagement = []
        self.next_opinion = False

    def share(self):
        """
        Defines the sharing behavior of nodes:
        Either has no opinion,
        shares disinformation,
        or fact checking information
        """

        self.engagement = []

        if rand.random() <= self.shares:
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
            prop = n_1 / len(all_opinions)
            if prop > self.prop_1:
                self.next_opinion = 1  # Disinformation
                self.status = "I"  # Infected
                self.resistance = True
            else:
                self.next_opinion = self.opinion
        else:
            self.next_opinion = self.opinion

        # Handle fact-checking logic (opinion 2)
        n_2 = count.get(2)
        if n_2:
            if rand.random() < self.prop_2:  # Will an Agent be immunised?
                self.resistance = True
                self.status = "R"
                self.next_opinion = 0

                if rand.random() < self.prop_vax:  # Will an Agent be immunised AND shares prebunking content?
                    self.next_opinion = 2
                    self.status = 'aR'
            else:
                self.next_opinion = self.opinion
        else:
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

    def attack(self, tick, kind=0, start=5, attack_length=5, decay=10):
        """
        [default]
        tick: (int)
            time steps in the model
        kind: (int)
            [0]: node shares no opinion
            1: node shares disinformation
            2: node shares fact-checking
        start: (int)
            [5]: beginning of the attack at time step
        attack_length: (int)
            [5]: duration of an attack in time steps
        decay: (int)
            [10]: decrease of attack intensity depending on which stereotype is used as blueprint for the dark agent's behavior
        """
        if self.dark:

            if kind == 0:  # Attack scenario 1: One single step with 50 times sharing (with p=0.5)
                if tick == start:
                    self.frequency = self.attack_frequency
                    self.share()
                    self.frequency = 1
                else:
                    self.share()

            elif kind == 1:  # Attack Scenario 2: The dark agent shares disinformation with an increasing volume
                # (10, 30, and 50 times) during three steps with a step of normal sharing behavior in between the attack steps.
                if tick == start:
                    self.active_attack = attack_length - 1
                    freq = self.attack_frequency
                    for a in range(self.active_attack):
                        if freq > 0:
                            freq -= decay
                    self.attack_frequency = freq
                    self.frequency = self.attack_frequency
                    self.share()
                    self.frequency = 1
                    self.pause = True

                else:
                    if self.active_attack:
                        if self.pause:
                            self.share()
                            self.pause = False
                        else:
                            self.attack_frequency += decay
                            self.frequency = self.attack_frequency
                            self.share()
                            self.frequency = 1
                            self.pause = True
                            self.active_attack -= 1
                            if self.active_attack < 1:
                                self.active_attack = False
                    else:
                        self.share()

            elif kind == 2:  # Attack scenario 3
                if tick == start:
                    self.active_attack = attack_length - 1
                    self.frequency = self.attack_frequency
                    self.share()
                    self.frequency = 1
                    self.pause = True

                else:
                    if self.active_attack:
                        if self.pause:
                            self.frequency = self.attack_frequency
                            self.share()
                            self.frequency = 1
                            self.pause = False
                        else:
                            if self.attack_frequency > 0:
                                self.attack_frequency -= decay

                            self.frequency = self.attack_frequency
                            self.share()
                            self.frequency = 1
                            self.pause = True
                            self.active_attack -= 1
                            if self.active_attack < 1:
                                self.active_attack = False
                    else:
                        self.share()

            else:
                self.share()

    def alter_agent(self, kind='dark', attack_strength=50):
        """
        Change the status of the agent
        [default]
        kind: (str)
            ['dark']: dark agent type
            'light': fact-checking sharing agent

        attack_strength: (int)
            [50]: intensity of the attack
        """

        if kind == 'dark':
            self.opinion = 1
            self.status = 'uI'
            self.shares = 1
            self.frequency = 1
            self.resistance = True
            self.dark = True
            self.attack_frequency = attack_strength

        elif kind == 'light':
            self.opinion = 2
            self.status = 'aR'
            self.shares = 1
            self.frequency = 1
            self.resistance = True
            self.dark = False
