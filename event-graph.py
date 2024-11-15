import pandas as pd
import networkx as nx
from pyvis.network import Network

# Load your data
file_path = 'path_to_your_file.csv'  # Replace with your file's path
data = pd.read_csv(file_path)

# Identify date columns and convert them
date_columns = [col for col in data.columns if pd.to_datetime(data[col], errors='coerce').notna().any()]
for col in date_columns:
    data[col] = pd.to_datetime(data[col], errors='coerce').dt.tz_localize(None)

# Create a directed graph and add nodes and edges
graph = nx.DiGraph()
for _, row in data.iterrows():
    events = row[date_columns].dropna().sort_values()
    for event in events:
        if event not in graph:
            graph.add_node(event, weight=0)
        graph.nodes[event]['weight'] += 1
    for i in range(len(events) - 1):
        event_from, event_to = events.iloc[i], events.iloc[i + 1]
        duration = (event_to - event_from).total_seconds()
        if graph.has_edge(event_from, event_to):
            edge_data = graph[event_from][event_to]
            edge_data['durations'].append(duration)
            edge_data['weight'] = sum(edge_data['durations']) / len(edge_data['durations'])
        else:
            graph.add_edge(event_from, event_to, durations=[duration], weight=duration)

# Use pyvis for visualization
net = Network(notebook=True, height="800px", width="100%", directed=True)

# Add nodes with size based on frequency
for node, attr in graph.nodes(data=True):
    net.add_node(str(node), title=str(node), size=attr['weight'] * 10, color="skyblue")

# Add edges with width based on average duration
for source, target, attr in graph.edges(data=True):
    net.add_edge(str(source), str(target), value=attr['weight'])

# Show the interactive graph
net.show("event_chronology_graph.html")
