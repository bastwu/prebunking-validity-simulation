import networkx as nx
from matplotlib import pyplot as plt, gridspec as gridspec, lines as lines


def draw_plot(node_list_start, tie_list_start, node_list_end, tie_list_end, e_s, e_i, e_r, n_s, n_i, n_r, n_ar, n_ui,
              custom_title, file_name):
    node_mult = 25  # magnification factor of nodes in the plot

    start_network = nx.DiGraph()
    start_network.add_nodes_from(node_list_start)
    start_network.add_edges_from(tie_list_start)

    status_dict = {
        "S": 'grey',
        "R": 'lightgreen',
        "aR": 'darkgreen',
        "I": 'pink',
        "uI": 'darkred'
    }

    colors = [status_dict[start_network.nodes[val]['status']] for val in start_network.nodes]
    degrees = [val * node_mult for (node, val) in start_network.degree()]

    lay = nx.spring_layout(start_network)  # , weight = 50)
    fig = plt.figure(figsize=(15, 15))
    gs = gridspec.GridSpec(3, 3, height_ratios=[1, .4, .4], width_ratios=[1, 1, .1])

    net_start = fig.add_subplot(gs[0])
    nx.draw_networkx_nodes(start_network, pos=lay, ax=net_start, node_size=degrees, node_color=colors, alpha=.75)
    nx.draw_networkx_edges(start_network, pos=lay, arrows=True, ax=net_start, node_size=degrees, alpha=.3)
    nx.draw_networkx_labels(start_network, pos=lay, font_size=8)
    net_start.set_title('a)', loc='left')

    end_network = nx.DiGraph()
    end_network.add_nodes_from(node_list_end)
    end_network.add_edges_from(tie_list_end)

    colors = [status_dict[end_network.nodes[val]['status']] for val in end_network.nodes]
    degrees = [val * node_mult for (node, val) in end_network.degree()]

    net_end = fig.add_subplot(gs[1])
    nx.draw_networkx_nodes(end_network, pos=lay, ax=net_end, node_size=degrees, node_color=colors, alpha=.75)
    nx.draw_networkx_edges(end_network, pos=lay, arrows=True, ax=net_end, node_size=degrees, alpha=.3)
    nx.draw_networkx_labels(end_network, pos=lay, font_size=8)
    net_end.set_title('b)', loc='left')

    net_legend = fig.add_subplot(gs[2])
    legend_elements = [
        lines.Line2D([0], [0], marker='o', color='w', markerfacecolor='grey', markersize=15, label='susceptible'),
        lines.Line2D([0], [0], marker='o', color='w', markerfacecolor='darkgreen', markersize=15,
                     label='prebunking agent'),
        lines.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightgreen', markersize=15, label='immunized'),
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

    fig.suptitle(custom_title)
    fig.tight_layout()

    fig.savefig(file_name, dpi=300)


def get_network(population):
    node_list = []
    tie_list = []
    for agent in population:
        node_list.append(agent.node_output())
        tie_list.extend(agent.tie_output())

    return node_list, tie_list
