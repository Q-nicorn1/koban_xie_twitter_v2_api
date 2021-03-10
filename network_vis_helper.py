import networkx as nx
from pyvis import network as net
import pyvis
import pandas as pd

def draw_graph(networkx_graph,notebook=True,output_filename='graph.html',show_buttons=False,only_physics_buttons=False):
        """
        This function accepts a networkx graph object,
        converts it to a pyvis network object preserving its node and edge attributes,
        and both returns and saves a dynamic network visualization.

        Valid node attributes include:
            "size", "value", "title", "x", "y", "label", "color".

            (For more info: https://pyvis.readthedocs.io/en/latest/documentation.html#pyvis.network.Network.add_node)

        Valid edge attributes include:
            "arrowStrikethrough", "hidden", "physics", "title", "value", "width"

            (For more info: https://pyvis.readthedocs.io/en/latest/documentation.html#pyvis.network.Network.add_edge)


        Args:
            networkx_graph: The graph to convert and display
            notebook: Display in Jupyter?
            output_filename: Where to save the converted network
            show_buttons: Show buttons in saved version of network?
            only_physics_buttons: Show only buttons controlling physics of network?
        """

        # import
        from pyvis import network as net

        # make a pyvis network
        pyvis_graph = net.Network(notebook=notebook)
        pyvis_graph.width = '950px'
        # for each node and its attributes in the networkx graph
        for node,node_attrs in networkx_graph.nodes(data=True):
            pyvis_graph.add_node(node,**node_attrs)

        # for each edge and its attributes in the networkx graph
        for source,target,edge_attrs in networkx_graph.edges(data=True):
            # if value/width not specified directly, and weight is specified, set 'value' to 'weight'
            if not 'value' in edge_attrs and not 'width' in edge_attrs and 'weight' in edge_attrs:
                # place at key 'value' the weight of the edge
                edge_attrs['value']=edge_attrs['weight']
            # add the edge
            pyvis_graph.add_edge(source,target,**edge_attrs)

        # turn buttons on
        if show_buttons:
            if only_physics_buttons:
                pyvis_graph.show_buttons(filter_=['physics'])
            else:
                pyvis_graph.show_buttons()

        # return and also save
        return pyvis_graph.show(output_filename)
    
def get_weighted_el(el):
    weighted_el = el.groupby(['author_screen_name_from', 'to', 'edge_type']).agg(len).reset_index()
    weighted_el = (weighted_el[['author_screen_name_from', 'to', 'edge_type', 'status_id']]
                              .rename(columns = {'author_screen_name_from': 'source', 'to': 'target', 'status_id':'weight'}))
    return weighted_el 

def render_graph(weighted_el, edge_type, edge_weight_threshold = 1):
    # filter el
    weighted_el = weighted_el[['source', 'target', 'weight']][(weighted_el['edge_type'] == edge_type) &
                                                              (weighted_el['weight'] >= edge_weight_threshold)]

    # creat graph object
    G = nx.from_pandas_edgelist(weighted_el, 'source', 'target', 'weight')
    
    # extract node list
    nl = pd.DataFrame({'name': list(G.nodes)})
    seed_nodes = weighted_el['source'].unique().tolist()
    target_nodes = weighted_el['target'].unique().tolist
    
    # calcualte node degree
    degree_list = list(G.degree)
    degree_list = [val[1] for val in degree_list]
    
    # assign attributes to a node list dataframe
    nl['color'] = 'lightgray'
    nl['color'][nl['name'].isin(seed_nodes)] = 'orange'
    nl['shape'] = 'dot'
    nl['shape'][nl['name'].isin(seed_nodes)] = 'square'
    nl['size'] = [str(4*x) for x in degree_list]
    nl['size'][nl['name'].isin(seed_nodes)] = '6'
    nl['size'] = nl['size'].astype(float)
    
    # assign attributes to the graph object
    node_attr = nl.set_index('name').to_dict('index')        
    nx.set_node_attributes(G, node_attr)
    nx.set_edge_attributes(G, 'gray', name ='color')
    
    # remove self loops
    G.remove_edges_from(nx.selfloop_edges(G))
    
    # draw the graph
    return draw_graph(G, show_buttons = True, only_physics_buttons=True) 