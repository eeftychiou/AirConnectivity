# Skeleton for Air Connectivity indicator
import json

import time
import math
import airctools as ac

import pandas as pd

import networkx as nx

import os.path

import matplotlib.pyplot as plt
import numpy as np

from igraph import Graph


import datetime as dt
from datetime import datetime


from bokeh.io import show, save
from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine
from bokeh.plotting import figure
from bokeh.plotting import from_networkx
from bokeh.palettes import Blues8, Reds8, Purples8, Oranges8, Viridis8, Spectral8
from bokeh.transform import linear_cmap

import settings

old_print = print

def timestamped_print(*args, **kwargs):
  old_print(datetime.now(), *args, **kwargs)

print = timestamped_print

def main():

    if settings.get('dataSource') == 0:
        airc_df = ac.load_raw_ECTL_flights(settings.get('dataSourceFname'), filterMarket = ["Traditional Scheduled", "Lowcost"], loadrows=settings.get('loadRows') )
        airc_df["Weight"] = 1.0

        if settings.get('sample') == 1:
            # Sample based on the sampleSize
            firstDateofTheMonth = airc_df['FILED_OFF_BLOCK_TIME'].iloc[0]
            day=settings['startDay']

            onDay = lambda dtinp, day: dtinp + dt.timedelta(days=(day - dtinp.weekday() - 1) % 7 + 1)

            StartDateTime = str(onDay(firstDateofTheMonth,day))
            EndDateTime = str(onDay(firstDateofTheMonth,day) + pd.Timedelta(days=(settings.get('sampleSize')+1)))   # Add one day to allow flights started to calculate onwards connectivity
            airc_df = airc_df.query(
                'FILED_OFF_BLOCK_TIME >= ' + "'" + StartDateTime + "'" + ' & FILED_OFF_BLOCK_TIME < ' + "'" + EndDateTime + "'")

            print("First "+ str(settings.get('sampleSize')) +  " days of the month:", airc_df.shape)

        if settings.get('edgeWeightConfig') == 0:   #simple weight connection
            airc_df["Weight"] = 1.0
        elif settings.get('edgeWeightConfig') == 1:  # edge weight depends on onwards connectivity
            airc_df=ac.add_weights(airc_df)
        else:
            # @TODO implement edge weight based on a/c capacity
            exit(-1)

        #get final dataframe based on the sample size
        if settings.get('sample') == 1:

            EndDateTime = str(onDay(firstDateofTheMonth,day) + pd.Timedelta(days=(settings.get('sampleSize'))))   # Add one day to allow flights started to calculate onwards connectivity
            airc_df = airc_df.query(
                'FILED_OFF_BLOCK_TIME >= ' + "'" + StartDateTime + "'" + ' & FILED_OFF_BLOCK_TIME < ' + "'" + EndDateTime + "'")

            print("Final Dataframe From: "+ StartDateTime +  " To:", EndDateTime)


    else:
        airc_df = ac.load_raw_processed_flights(settings.get('dataSourceFname'),filterMarket =None, loadrows = settings.get('loadRows'))


    print( "Saving CSV result ", str(airc_df.shape[0]) , 'x ' + str(airc_df.shape[1]) )
    dateNow = datetime.now().strftime("%Y%m%d_%H%M%S")

    fname = 'data/Result_(' + dateNow +  ')_' + settings.get("dataSourceFname")
    airc_df.to_csv(fname, index=False)

    print("Generating Graph")
    # Generate nxGraph
    final_df = airc_df.groupby(['ADEP','ADES'],as_index=False).Weight.sum()
    nx_airc_G = nx.from_pandas_edgelist(final_df, source='ADEP', target='ADES', edge_attr='Weight',
                                        create_using=nx.DiGraph())

    fname = 'data/gexf_(' + dateNow +  ')_' + settings.get("dataSourceFname")+ '.gexf'
    if not os.path.isfile(fname):
        nx.write_gexf(nx_airc_G, fname)

    fname = 'data/GraphPickle_(' + dateNow + ')_' + settings.get("dataSourceFname")
    nx.write_gpickle(nx_airc_G, fname)

    # Calculate Statistics
    print( "Calculating Statistics")
    # ig_pagerank= ig_airc_G.pagerank(weights='Weight')
    pagerank = dict(nx.pagerank(nx_airc_G, alpha=0.85, weight='Weight'))
    degrees = dict(nx.degree(nx_airc_G))

    afname = 'data/Sept_pagerank_' + str(airc_df.shape[0]) + '_' + str(airc_df.shape[1]) + '.json'
    bfname = 'data/Sept_degrees_' + str(airc_df.shape[0]) + '_' + str(airc_df.shape[1]) + '.json'
    a_file = open(afname, "w")
    b_file = open(bfname, "w")

    json.dump(pagerank, a_file)
    json.dump(degrees, b_file)

    a_file.close()
    b_file.close()
    print("Done Calculating Statistics")

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

    # Choose a title!
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
    settings.init()

    settings['dataSource'] = 0                                      # 0 for raw , 1 for processed
    settings['dataSourceFname'] = 'Flights_20180901_20180930.csv'   # filename of data
    settings['edgeWeightConfig'] = 1                                # 0 for simple connections, 1 for onwards connectivity 2 for passenger numbers
    settings['sample'] = 1                                          # 0 whole month,  1 sampleSize days sample
    settings['startDay'] = 0                                         # 0-7 starting with Monday
    settings['sampleSize'] = 14                                       # Sample size in days
    settings['loadRows'] = 1000000
    settings['minLayover'] = 30                                        # minimum layover time in min for connecting flights
    settings['maxLayover'] = 240                                  # minimum layover time in min for connecting flights

    main()
