import random as rand
import numpy as np
from collections import Counter
import Agent
from plotResults import draw_plot, get_network


def create_population(verbose, pop_size, prob_share_indifferent, prob_prebunk, prob_immune, n_friends, n_add, dark_quantile):

    if verbose:
        print('Initializing population...')

    population = []
    for i in range(pop_size):
        agent = Agent.Agent(prob_prebunk, i, prob_share_indifferent, prob_immune)
        population.append(agent)

    chosen = population.copy()  # Helper List for already chosen Agents as friends;at the beginning every Agent exists
    # exactly one time in the chosen-list

    if verbose:
        print('initializing friends')

    for i in range(n_friends):
        for agent in population:
            n_friends = i + 1
            while len(agent.friends) < n_friends:
                fr = rand.choice(chosen)
                if fr != agent and fr not in agent.friends:
                    agent.friends.append(fr)
                    # If an agent is chosen as a friend, the agent is added 5 more times to the chosen-list
                    # (because of 'preferential attachment'):
                    chosen.extend([fr] * n_add)

    if verbose:
        print('initializing light and dark')
    light = Counter(chosen).most_common(1)[0][0]

    incoming_edges = Counter(chosen)
    n_list = list(incoming_edges.values())
    med_in = np.quantile(n_list, dark_quantile, method='nearest')
    m_list = [c for c, v in incoming_edges.items() if v == med_in]

    dark = rand.choice(m_list)  # choose an Agent as dark Agent from the List of agents within the 0.75 quantile

    light.alter_agent('light')
    dark.alter_agent('dark')

    return population


def get_opinion_shares_and_agent_proportion(population):
    # Count statuses and initialize counters for engagement
    status_counts = Counter(agent.status for agent in population)
    engagement_counts = Counter()

    # Iterate to count opinions and clear engagements
    for agent in population:
        engagement_counts[agent.opinion] += len(agent.engagement)
        agent.engagement = []  # Clear engagement after counting

    # Extract counts for statuses
    ns = status_counts["S"]
    ni = status_counts["I"]
    nr = status_counts["R"]
    nar = status_counts["aR"]
    nui = status_counts["uI"]

    # Safety check for unexpected statuses
    valid_statuses = {"S", "I", "R", "uI", "aR"}
    if any(status not in valid_statuses for status in status_counts):
        raise ValueError("Unexpected status encountered in population.")

    # Extract counts for engagements
    es = engagement_counts[0]  # Opinion 0
    ei = engagement_counts[1]  # Opinion 1
    er = engagement_counts[2]  # Opinion 2

    return es, ei, er, ns, ni, nr, nar, nui


def run_model(
        pop_size,
        n_ticks,
        n_friends,
        n_add,
        prob_share_indifferent,
        prob_share_disinfo,
        prob_share_facts,

        attack_start,
        attack_kind,
        dark_quantile,

        prob_prebunk,
        prob_immune,

        draw=False,
        verbose=False,
        dry_run=False,
        custom_title='Title',
        file_name='savefig'
):
    """
    Simulate the user network with the defined properties
    [default]
    pop_size: (int)
        number of the nodes in the user networks
    n_ticks: (int)
        number of time steps conducted in the simulation
    n_friends: (int)
        maximum number of friends a user can have
    n_add: (int)
        Number of times an agent to which an edge is established should be added to the list of already selected target
        agents (necessary for preferential attachment)
    prob_share_indifferent: (float)
        probability to share a node's opinion with its neighbour if its opinion is indifferent
    prob_share_disinfo: (float)
        probability to share a node's opinion with its neighbour if its opinion is disinformation
    prob_share_facts: (float)
        probability to share a node's opinion with its neighbour if its opinion is prebunking
    attack_start: (int)
        time step when the attacks start
    attack_kind: (int)
        type of attack executed by the dark agents, i.e., which kind of stereotype is used as blueprint
    dark_quantile: (float)
        percentile of in-degrees of edges that determines which node is the dark agent
    prob_prebunk: (float)
        a node's probability to become a prebunking agent themselves
    prob_immune: (float)
        a node's probability to change their status to resistant
    draw: (bool)
        after the simulation concluded, should a plot be created?
    verbose: (bool)
        should the status of the simulation be updated in the console?
    dry_run: (bool)
        for testing purposes, no run of the simulation, only for parameter testing
    custom_title: (str)
        the title of the plot
    file_name: (str)
        the name of the file the plot is stored into
    """
    if dry_run:
        print('Dry run with: ', 'Size: ', pop_size, 'Ticks: ', n_ticks,
              'Sharing: ', prob_share_indifferent, prob_share_disinfo, prob_share_facts,
              'Attack: ', attack_kind,
              'Dark quant: ', dark_quantile,
              'Prob pre: ', prob_prebunk,
              'Prob imu: ', prob_immune)
        return {}, {}, {}

    if verbose:
        print('create population')
    population = create_population(verbose, pop_size,
                                   prob_share_indifferent,
                                   prob_prebunk, prob_immune,
                                   n_friends,
                                   n_add,
                                   dark_quantile)
    if draw:
        start_node_list, start_tie_list = get_network(population)

    e_s = []
    e_i = []
    e_r = []
    n_s = []
    n_i = []
    n_r = []
    n_ar = []
    n_ui = []

    if verbose:
        print('run model')

    for tick in range(n_ticks):
        es, ei, er, ns, ni, nr, nar, nui = get_opinion_shares_and_agent_proportion(population)
        e_s.append(es)
        e_i.append(ei)
        e_r.append(er)
        n_s.append(ns)
        n_i.append(ni)
        n_r.append(nr)
        n_ar.append(nar)
        n_ui.append(nui)

        for agent in population:
            if agent.dark:
                agent.attack(tick, attack_kind, attack_start)
            else:
                agent.share()

        for agent in population:
            agent.check_friends()

        for agent in population:
            agent.update_opinion(prob_share_indifferent, prob_share_disinfo, prob_share_facts)

    if draw:
        end_node_list, end_tie_list = get_network(population)
        if verbose:
            print('draw plot')
        draw_plot(start_node_list, start_tie_list, end_node_list, end_tie_list, e_s, e_i, e_r, n_s, n_i, n_r, n_ar,
                  n_ui, custom_title, file_name)

    count_s = n_s[-1]
    count_i = n_i[-1] + n_ui[-1]
    count_r = n_r[-1] + n_ar[-1]

    info_dict_end = dict(
        n_s=count_s,
        n_i=count_i,
        n_r=count_r
    )
    info_dict_shares = dict(
        s=e_s,
        i=e_i,
        r=e_r
    )

    info_dict_status = dict(
        s=n_s,
        i=n_i,
        r=n_r,
        ar=n_ar,
        ui=n_ui
    )

    if verbose:
        print(info_dict_end)

    return info_dict_end, info_dict_shares, info_dict_status
