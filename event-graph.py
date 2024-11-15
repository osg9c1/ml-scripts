import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Load your CSV file
file_path = 'path_to_your_file.csv'  # Replace with your file's path
data = pd.read_csv(file_path)

# Identify date columns
date_columns = [col for col in data.columns if pd.to_datetime(data[col], errors='coerce').notna().any()]

# Convert date columns to datetime
for col in date_columns:
    data[col] = pd.to_datetime(data[col], errors='coerce')

# Create the graph
graph = nx.DiGraph()

# Process the rows to create nodes and edges
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

# Clean up durations for visualization
for edge in graph.edges(data=True):
    edge[2].pop('durations', None)

# Plot the graph
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(graph)
nx.draw(graph, pos, with_labels=True, node_size=[graph.nodes[node]['weight'] * 50 for node in graph.nodes],
        font_size=8, node_color="skyblue", edge_color="gray")
labels = nx.get_edge_attributes(graph, 'weight')
nx.draw_networkx_edge_labels(graph, pos, edge_labels={k: f"{v:.2f}s" for k, v in labels.items()})
plt.title("Event Chronology Graph")
plt.show()
