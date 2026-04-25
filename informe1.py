import torch
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import iplotx as ipx
import scipy as sp
from torch_geometric.data import Data
from torch_geometric.utils import to_networkx

ROUTES_AMOUNT = 100 # borrar si se quieren ocupar todos

stops = pd.read_csv("data/stop_times.txt") #GTFS Data está guardada en carpeta data
stops = pd.DataFrame(stops)

trips = pd.read_csv("data/trips.txt") 
trips = pd.DataFrame(trips)

routes = pd.read_csv("data/routes.txt") 
routes = pd.DataFrame(routes)

stops = stops.drop(['arrival_time', 'departure_time', 'pickup_type', 'drop_off_type', 'timepoint'], axis=1)
dt = stops.merge(trips[['route_id', 'trip_id']],
    left_on= 'trip_id',
    right_on='trip_id',
    how='left')

dt = dt.drop(['trip_id'], axis=1)
dt = dt.drop_duplicates()
metro_list = ['L1', 'L2', 'L3', 'L4', 'L4A', 'L5', 'L6', 'BA', 'MTR', 'MTN']
metro = dt[dt['route_id'].isin(metro_list)].index
dt.drop(metro, inplace=True)

result = dt.groupby('route_id')['stop_id'].unique().reset_index()

result = result.merge(routes[['route_id', 'route_color', 'route_text_color']],
    left_on= 'route_id',
    right_on='route_id',
    how='left')
result['route_color'] = '#' + result['route_color'].astype(str)
result['route_text_color'] = '#' + result['route_text_color'].astype(str)
if ROUTES_AMOUNT > 0:
    result = result.head(ROUTES_AMOUNT)

stops_nodes = result.to_dict('index')


nice_nodes = []

for i in range(0, len(stops_nodes)):
    for j in range(i+1, len(stops_nodes)):
        if set(stops_nodes[i]['stop_id']) & set(stops_nodes[j]['stop_id']):
            nice_nodes.append([stops_nodes[i]['route_id'], stops_nodes[j]['route_id']])
            nice_nodes.append([stops_nodes[j]['route_id'], stops_nodes[i]['route_id']])


G = nx.Graph()
G.add_nodes_from(result['route_id'])
G.add_edges_from(nice_nodes)

node_colors = result['route_color'].to_list()
text_colors = result['route_text_color'].to_list()

layout = nx.kamada_kawai_layout(G)
ipx.network(G, 
    layout=layout,
    edge_shrink=3,
    edge_alpha=0.1,
    vertex_facecolor=node_colors,
    node_label_color=text_colors,
    node_labels=True,
    figsize=(8,8),
    title='Interconexión recorridos RED'
    )

plt.savefig('figure1.png', dpi=300, transparent=False, bbox_inches='tight')