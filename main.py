# Skeleton for Air Connectivity indicator
import json
from time import strftime, gmtime
import time
import math
import airctools as ac

import pandas as pd
import community as community_louvain
import networkx as nx
import igraph as ig
import os.path


import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from igraph import Graph

from bokeh.io import show, save
from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine
from bokeh.plotting import figure
from bokeh.plotting import from_networkx
from bokeh.palettes import Blues8, Reds8, Purples8, Oranges8, Viridis8, Spectral8
from bokeh.transform import linear_cmap



def main():


    airc_df = ac.load_raw_ECTL_flights('Flights_20180901_20180930.csv')

    airc_df["Weight"] = 1.0
    for i, row in airc_df.iterrows():
        DestinationDepartureTime = datetime.strftime(row['FILED_ARRIVAL_TIME'] + pd.Timedelta(minutes=30), '%Y-%m-%d %H:%M:%S')
        DestinationMaxDepartureTime = datetime.strftime(row['FILED_ARRIVAL_TIME'] + pd.Timedelta(minutes=120),
                                                   '%Y-%m-%d %H:%M:%S')

        DestinationAirport= '"'+ row['ADES'] + '"'
        DepartureAirport= '"'+ row['ADEP']  + '"'

        EdgeWeight = len(airc_df.query('ADEP == ' + DestinationAirport + ' & FILED_OFF_BLOCK_TIME >= ' + "'" + DestinationDepartureTime + "'" + ' & FILED_OFF_BLOCK_TIME <= ' + "'" + DestinationMaxDepartureTime + "'" )) + 1

        airc_df.at[i, 'Weight'] = EdgeWeight

        if i%10000==0:
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()),"Processed:",i)



    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()), "Saving CSV result")
    fname = 'data/Sept_' + str(airc_df.shape[0]) + '_' + str(airc_df.shape[1]) + '.csv'
    airc_df.to_csv(fname, index=False)


    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()),"Generating Graph")
    # Generate nxGraph
    nx_airc_G = nx.from_pandas_edgelist(airc_df, source='ADEP', target='ADES', edge_attr='Weight', create_using=nx.DiGraph())
    fname = 'data/airCon_' +  str(airc_df.shape[0]) + '.gexf'
    if not os.path.isfile(fname):
        nx.write_gexf(nx_airc_G, fname)



    #ig_airc_G = Graph.DataFrame(airc_df[['ADEP', 'ADES', 'Weight']], directed=True)
    #ig_airc_G = ig.Graph.from_networkx(nx_airc_G)

    #nx.write_gpickle(nx_airc_G, "test.gpickle")

    #Calculate Statistics

    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()),"Calculating Statistics")
    #ig_pagerank= ig_airc_G.pagerank(weights='Weight')
    pagerank = dict(nx.pagerank(nx_airc_G, alpha=0.85, weight='Weight'))
    degrees = dict(nx.degree(nx_airc_G))

    afname = 'data/Sept_pagerank_' + str(airc_df.shape[0])  + '_' + str(airc_df.shape[1]) + '.json'
    bfname = 'data/Sept_degrees_' + str(airc_df.shape[0])  + '_' + str(airc_df.shape[1]) + '.json'
    a_file = open(afname, "w")
    b_file = open(bfname, "w")

    json.dump(pagerank, a_file)
    json.dump(degrees, b_file)

    a_file.close()
    b_file.close()
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()), "Done Calculating Statistics")

    exit(0)

    nx.set_node_attributes(nx_airc_G, name='degree', values=degrees)
    nx.set_node_attributes(nx_airc_G, name='pagerank', values=pagerank)

    number_to_adjust_by = 5
    adjusted_node_size = dict([(node, degree + number_to_adjust_by) for node, degree in nx.degree(nx_airc_G)])
    nx.set_node_attributes(nx_airc_G, name='adjusted_node_size', values=adjusted_node_size)

    # Choose attributes from G network to size and color by — setting manual size (e.g. 10) or color (e.g. 'skyblue') also allowed
    size_by_this_attribute = 'adjusted_node_size'
    color_by_this_attribute = 'adjusted_node_size'

    # Pick a color palette — Blues8, Reds8, Purples8, Oranges8, Viridis8
    color_palette = Blues8

    #Choose a title!
    title = 'September 2018 Eurocontrol Dataset'

    # Establish which categories will appear when hovering over each node
    HOVER_TOOLTIPS = [
        ("Airport", "@index"),
        ("Degree", "@degree"),
        ("Pagerank", "@pagerank")
    ]

    # Create a plot — set dimensions, toolbar, and title
    plot = figure(tooltips=HOVER_TOOLTIPS,
                  tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
                  x_range=Range1d(-30.1, 30.1), y_range=Range1d(-30.1, 30.1), title=title)

    # Create a network graph object
    # https://networkx.github.io/documentation/networkx-1.9/reference/generated/networkx.drawing.layout.spring_layout.html\
    network_graph = from_networkx(nx_airc_G, nx.spring_layout, scale=10, center=(0, 0))

    # Set node sizes and colors according to node degree (color as spectrum of color palette)
    minimum_value_color = min(network_graph.node_renderer.data_source.data[color_by_this_attribute])
    maximum_value_color = max(network_graph.node_renderer.data_source.data[color_by_this_attribute])
    network_graph.node_renderer.glyph = Circle(size=size_by_this_attribute,
                                               fill_color=linear_cmap(color_by_this_attribute, color_palette,
                                                                      minimum_value_color, maximum_value_color))

    # Set edge opacity and width
    network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=1)

    plot.renderers.append(network_graph)

    show(plot)




if __name__ == '__main__':
    main()


