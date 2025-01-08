import networkx as nx
import random as rand
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as lines
import matplotlib.gridspec as gridspec
from collections import Counter
import Agent


def create_population(verbose, pop_size, prob_share, prebunk_prob, prob_immune, n_friends, n_add, dark_quantile,
                      atk_str, draw, node_mult):
    # Create the population
    if verbose:
        print('initializing population')

    population = []
    chosen = []  # helper List for already chosen Agents as friends
    for i in range(pop_size):  #
        node_id = i
        shares = prob_share
        agent = Agent.Agent(prebunk_prob, node_id, shares, prob_immune)

        population.append(agent)
        chosen.append(agent)  # At the beginning every Agent exists exactly one time in the chosen-list

    if verbose:
        print('initializing friends')
    for i in range(n_friends):
        for agent in population:
            n_friends = i + 1
            while len(agent.friends) < n_friends:
                fr = rand.choice(chosen)
                if fr == agent:
                    continue
                elif fr in agent.friends:
                    continue
                else:
                    agent.friends.append(fr)
                    for k in range(n_add):
                        chosen.append(
                            fr)  # If an agent is chosen as a friend, the agent is added 5 more times to the chosen-list (because of 'preferential attachment')

    if verbose:
        print('initializing light and dark')
    light = Counter(chosen).most_common(1)[0][0]

    c = Counter(chosen)
    n_list = []
    for k in c.keys():  # k should be an agent
        n_list.append(c[k])  # n_list is just a list of each agents number of incoming edges
    med_in = np.quantile(n_list, dark_quantile, method='nearest')
    m_list = []
    for k in c.keys():
        if c[k] == med_in:
            m_list.append(k)

    dark = rand.choice(m_list)  # choose an Agent as dark Agent from the List of agents within the 0.75 quantile

    light.alter_agent('light')
    dark.alter_agent('dark', attack_strength=atk_str)

    if verbose:
        print('initial plots')
    node_list = []
    tie_list = []
    for agent in population:
        node_list.append(agent.node_output())
        tie_list.extend(agent.tie_output())

    if draw:
        g = nx.DiGraph()
        g.add_nodes_from(node_list)
        g.add_edges_from(tie_list)

        status_dict = {
            "S": 'grey',
            "R": 'lightgreen',
            "aR": 'darkgreen',
            "I": 'red',
            "uI": 'darkred'
        }

        colors = [status_dict[g.nodes[val]['status']] for val in g.nodes]
        degrees = [val * node_mult for (node, val) in g.degree()]
        lay = nx.spring_layout(g)  # , weight = 50)
        fig = plt.figure(figsize=(15, 15))
        gs = gridspec.GridSpec(3, 3, height_ratios=[1, .4, .4], width_ratios=[1, 1, .1])

        n_s = []
        n_i = []
        n_r = []
        n_ui = []
        n_ar = []

        e_s = []
        e_i = []
        e_r = []

        ns = 0
        ni = 0
        nr = 0
        nar = 0
        nui = 0

        for agent in population:
            if agent.status == 'S':
                ns += 1
            elif agent.status == 'I':
                ni += 1
            elif agent.status == 'R':
                nr += 1
            elif agent.status == 'uI':
                nui += 1
            elif agent.status == 'aR':
                nar += 1
            else:
                raise ValueError

        n_s.append(ns)
        n_i.append(ni)
        n_r.append(nr)
        n_ar.append(nar)
        n_ui.append(nui)

        es = 0
        ei = 0
        er = 0

        e_s.append(es)
        e_i.append(ei)
        e_r.append(er)

        net_start = fig.add_subplot(gs[0])
        nx.draw_networkx_nodes(g, pos=lay, ax=net_start, node_size=degrees, node_color=colors, alpha=.75)
        nx.draw_networkx_edges(g, pos=lay, arrows=True, ax=net_start, node_size=degrees, alpha=.3)
        nx.draw_networkx_labels(g, pos=lay, font_size=8)
        net_start.set_title('a)', loc='left')

    if verbose:
        print('run model')

    return population, n_s, n_i, n_r, n_ui, n_ar, e_s, e_i, e_r, fig, gs, lay


def run_model(
        pop_size=100,
        n_ticks=20,
        n_friends=5,
        n_add=5,
        prob_share=.5,

        attack_start=5,
        attack_kind=0,
        atk_len=5,
        atk_str=50,
        decay=10,
        dark_quantile=.75,

        prebunk_prob=1.0,
        prob_immune=0.0,

        # For graphics
        node_mult=50,

        draw=True,
        verbose=True,

        custom_title='Title',
        file_name='savefig'
):
    """
    Simulate the user network with the defined properties
    [default]
    pop_size: (int)
        [100]:number of the nodes in the user networks
    n_ticks: (int)
        [20]: number of time steps conducted in the simulation
    n_friends: (int)
        [5]: maximum number of friends a user can have
    n_add: (int)
        [5]: Number of times an agent to which an edge is established should be added to the list of already selected target agents
    prob_share: (float)
        [0.5]: probability to share a node's opinion with its neighbour
    attack_start: (int)
        [5]: time step when the attacks start
    attack_kind: (int)
        [0]: type of attack executed by the dark agents, i.e., which kind of stereotype is used as blueprint
    atk_len: (int)
        [5]: time steps the attack lasts
    atk_str: (int)
        [50]: number of messages shared during an attack
    decay: (int)
        [10]: decrease of attack intensity depending on which stereotype is used as blueprint for the dark agent's behavior
    dark_quantile: (float)
        [0.75]: percentile of in-degrees of edges that determines which node is the dark agent
    prebunk_prob: (float)
        [1.0]: a node's probability to become a prebunking agent themselves
    prob_immune: (float)
        [0.0]: a node's probability to change their status to resistant
    node_mult: ()
        [5]: magnification factor of nodes in the plot
    draw: (bool)
        [True]: after the simulation concluded, should a plot be created?
    verbose: (bool)
        [True]: should the status of the simulation be updated in the console?
    custom_title: (str)
        ['Title']: the title of the plot
    file_name: (str)
        ['savefig']: the name of the file the plot is stored into
    """
    population, n_s, n_i, n_r, n_ui, n_ar, e_s, e_i, e_r, fig, gs, lay = create_population(verbose, pop_size,
                                                                                           prob_share,
                                                                                           prebunk_prob, prob_immune,
                                                                                           n_friends,
                                                                                           n_add,
                                                                                           dark_quantile, atk_str, draw,
                                                                                           node_mult)

    for tick in range(n_ticks):

        for agent in population:
            if agent.dark:
                agent.attack(tick=tick, kind=attack_kind, start=5, attack_length=atk_len, decay=decay)
            else:
                agent.share()

        for agent in population:
            agent.check_friends()

        for agent in population:
            agent.update_opinion()

        # The code below is solely for plotting purposes
        if draw:
            ns = 0
            ni = 0
            nr = 0
            nui = 0
            nar = 0

            # S, I, uI, R, aR

            for agent in population:
                if agent.status == 'S':
                    ns += 1
                elif agent.status == 'I':
                    ni += 1
                elif agent.status == 'R':
                    nr += 1
                elif agent.status == 'uI':
                    nui += 1
                elif agent.status == 'aR':
                    nar += 1
                else:
                    raise ValueError

            es = 0
            ei = 0
            er = 0

            for agent in population:
                if agent.opinion == 0:
                    # ns+=1
                    es += len(agent.engagement)
                    agent.engagement = []
                elif agent.opinion == 1:
                    # ni+=1
                    ei += len(agent.engagement)
                    agent.engagement = []
                elif agent.opinion == 2:
                    # nr+=1
                    er += len(agent.engagement)
                    agent.engagement = []

            n_s.append(ns)
            n_i.append(ni)
            n_r.append(nr)
            n_ar.append(nar)
            n_ui.append(nui)

            e_s.append(es)
            e_i.append(ei)
            e_r.append(er)

    if draw:
        node_list = []
        tie_list = []
        for agent in population:
            node_list.append(agent.node_output())
            tie_list.extend(agent.tie_output())

        g = nx.DiGraph()
        g.add_nodes_from(node_list)
        g.add_edges_from(tie_list)

        status_dict = {
            "S": 'grey',
            "R": 'lightgreen',
            "aR": 'darkgreen',
            "I": 'pink',
            "uI": 'darkred'
        }

        colors = [status_dict[g.nodes[val]['status']] for val in g.nodes]
        degrees = [val * node_mult for (node, val) in g.degree()]

        net_end = fig.add_subplot(gs[1])
        nx.draw_networkx_nodes(g, pos=lay, ax=net_end, node_size=degrees, node_color=colors, alpha=.75)
        nx.draw_networkx_edges(g, pos=lay, arrows=True, ax=net_end, node_size=degrees, alpha=.3)
        nx.draw_networkx_labels(g, pos=lay, font_size=8)
        net_end.set_title('b)', loc='left')

        net_legend = fig.add_subplot(gs[2])
        legend_elements = [
            lines.Line2D([0], [0], marker='o', color='w', markerfacecolor='grey', markersize=15, label='susceptible'),
            lines.Line2D([0], [0], marker='o', color='w', markerfacecolor='darkgreen', markersize=15,
                         label='prebunking agent'),
            lines.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightgreen', markersize=15,
                         label='immunized'),
            lines.Line2D([0], [0], marker='o', color='w', markerfacecolor='darkred', markersize=15, label='dark agent'),
            lines.Line2D([0], [0], marker='o', color='w', markerfacecolor='pink', markersize=15, label='infected'),
        ]

        net_legend.legend(handles=legend_elements, loc='upper left')
        net_legend.axis('off')

        vol_share = fig.add_subplot(gs[3:5])

        vol_share.plot(e_s, color='grey')
        vol_share.plot(e_i, color='red')
        vol_share.plot(e_r, color='green')
        vol_share.set_title('c)', loc='left')
        vol_share.set_xlabel('model steps', loc='center')
        vol_share.set_ylabel('shares')

        vol_share_legend = fig.add_subplot(gs[5])
        legend_elements = [lines.Line2D([0], [0], color='grey', lw=4, label='opinion 0'),
                           lines.Line2D([0], [0], color='red', lw=4, label='opinion 1'),
                           lines.Line2D([0], [0], color='green', lw=4, label='opinion 2')]
        vol_share_legend.legend(handles=legend_elements, loc='upper left')
        vol_share_legend.axis('off')

        n_agents = fig.add_subplot(gs[6:8])

        n_agents.plot(n_s, color='grey')
        n_agents.plot(n_i, color='pink')
        n_agents.plot(n_r, color='lightgreen')
        n_agents.plot(n_ar, color='darkgreen')
        n_agents.plot(n_ui, color='darkred')
        n_agents.set_title('d)', loc='left')
        n_agents.set_xlabel('model steps', loc='center')
        n_agents.set_ylabel('proportion of agents (%)')

        n_agents_legend = fig.add_subplot(gs[8])
        legend_elements = [
            lines.Line2D([0], [0], color='grey', lw=4, label='susceptible'),
            lines.Line2D([0], [0], color='darkgreen', lw=4, label='prebunking agent'),
            lines.Line2D([0], [0], color='lightgreen', lw=4, label='immunized'),
            lines.Line2D([0], [0], color='darkred', lw=4, label='dark agent'),
            lines.Line2D([0], [0], color='pink', lw=4, label='infected'),
        ]

        # Create the figure
        n_agents_legend.legend(handles=legend_elements, loc='upper left')
        n_agents_legend.axis('off')

    if draw:
        fig.suptitle(custom_title)
        fig.tight_layout()

        fig.savefig(file_name, dpi=300)

    count_s = 0
    count_i = 0
    count_r = 0
    for agent in population:
        if agent.status == 'S':
            count_s += 1
        elif agent.status == 'I':
            count_i += 1
        elif agent.status == 'uI':
            count_i += 1
        elif agent.status == 'R':
            count_r += 1
        elif agent.status == 'aR':
            count_r += 1
        else:
            raise ValueError

    info_dict = dict(
        pop_size=pop_size,
        n_ticks=n_ticks,
        n_friends=n_friends,
        n_add=n_add,

        attack_start=attack_start,
        attack_kind=attack_kind,
        dark_quantile=dark_quantile,

        prebunk_prob=prebunk_prob,
        vax_prob=prob_immune,

        n_s=count_s,
        n_i=count_i,
        n_r=count_r
    )

    if verbose:
        print(info_dict)

    return info_dict
