# import pandas as pd
# import networkx as nx
# from pyvis.network import Network
# import os
# # Load your data
# file_path = "../Downloads/event_graph_2.csv"  # Replace with your file path
# data = pd.read_csv(file_path)
#
# # Identify columns for filtering and processing
# vehicle_type_column = "VEHICLE_TYPE"
# date_columns = [col for col in data.columns if "DT_" in col]
#
# # Convert date columns to datetime
# for col in date_columns:
#     data[col] = pd.to_datetime(data[col], errors="coerce")
#
# # Function to build the graph for a specific vehicle type
# def build_graph(vehicle_type=None):
#     # Filter data by vehicle type
#     if vehicle_type and vehicle_type != "All":
#         filtered_data = data[data[vehicle_type_column] == vehicle_type]
#     else:
#         filtered_data = data
#
#     # Create the graph
#     graph = nx.DiGraph()
#
#     # Add nodes with weights (count of non-null entries)
#     sorted_columns = sorted(date_columns, key=lambda col: data[col].min())
#     for col in sorted_columns:
#         weight = filtered_data[col].notna().sum()
#         graph.add_node(col, weight=weight)
#
#     # Add edges with mean durations as weights
#     for _, row in filtered_data.iterrows():
#         events = row[date_columns].dropna().sort_values()
#         for i in range(len(events) - 1):
#             source, target = events.index[i], events.index[i + 1]
#             duration = (events.iloc[i + 1] - events.iloc[i]).total_seconds() / (24 * 3600)
#             if graph.has_edge(source, target):
#                 graph[source][target]["weight"] += 1
#                 graph[source][target]["mean_duration"] = (
#                     graph[source][target]["mean_duration"] + duration
#                 ) / 2
#             else:
#                 graph.add_edge(source, target, weight=1, mean_duration=duration)
#
#     return graph
#
# # Function to add nodes and edges to Pyvis Network
# def add_to_network(graph, net):
#     for node, attr in graph.nodes(data=True):
#         net.add_node(
#             node,
#             label=f"{node}",
#             shape="box",  # Use a box shape for better readability
#             color="lightblue",
#             font={"size": 14}
#         )
#
#     sorted_edges = sorted(graph.edges(data=True), key=lambda x: x[2]['weight'], reverse=True)
#
#     for source, target, attr in sorted_edges:
#         if attr['weight'] > 1:
#             net.add_edge(
#                 source,
#                 target,
#                 label=f"{int(attr['mean_duration'])} days",
#                 color="gray",
#                 font={"size": 14, "align": "top"},
#                 smooth={"type": "curvedCW"},  # Use curved edges for better separation
#                 arrows={"to": {"enabled": True, "scaleFactor": 1.2}}
#             )
#             print(f"Source:{source} target:{target} weight:{attr['weight']}, mean_duration:{int(attr['mean_duration'])} days")
# # Build the initial graph for "All" vehicle types
# graph = build_graph(vehicle_type="All")
#
# # Debugging nodes and edges
#
#
# # Create Pyvis Network
# net = Network(height="800px", width="100%", directed=True, cdn_resources="in_line")
# # net.barnes_hut(
# #     gravity=-2000,
# #     spring_length=200,
# #     spring_strength=0.05,
# #     damping=0.1
# # )
# # net.repulsion(
# #     node_distance=250,
# #     central_gravity=0.3,
# #     spring_length=200,
# #     spring_strength=0.05,
# #     damping=0.09
# # )
# net.set_options("""
# {
#   "layout": {
#     "hierarchical": {
#       "enabled": true,
#       "direction": "UD",
#       "sortMethod": "directed",
#       "nodeSpacing": 300,
#       "treeSpacing": 400
#     }
#   },
#   "physics": {
#     "enabled": false
#   },
#   "barnes_hut":{
#   "gravity": -2000,
#   "spring_length":200,
#   "spring_strength":0.05,
#   "damping":0.1
#   },
#   "repulsion":{
#   "node_distance":250,
#   "central_gravity":0.3,
#   "spring_length": 200,
#   "spring_strength":0.05,
#   "damping":0.09
#   }
#
# }
# """)
#
#
#
# # Add nodes and edges
# add_to_network(graph, net)
#
# # Save and display the HTML
# net.save_graph("fleet_maintenance_process.html")
#
# # Export to Gephi for further analysis
# nx.write_graphml(graph, "fleet_maintenance_process.graphml")
# print("Graph exported to Gephi format.")

import pandas as pd
from pyvis.network import Network
import networkx as nx

# Load your data from a file (Update the file path)
data = pd.read_csv('../Downloads/event_graph_2.csv')  # Replace with your actual file path

# Parse datetime columns
date_columns = [col for col in data.columns if col.startswith('DT_')]
for col in date_columns:
    data[col] = pd.to_datetime(data[col], errors='coerce')

# Define the vehicle type filter in the HTML
vehicle_types = data['VEHICLE_TYPE'].unique()
data['VEHICLE_TYPE'] = data['VEHICLE_TYPE'].fillna('Unknown')


# Build the graph
def build_graph(data, vehicle_type='All'):
    filtered_data = data if vehicle_type == 'All' else data[data['VEHICLE_TYPE'] == vehicle_type]
    graph = nx.DiGraph()

    for _, row in filtered_data.iterrows():
        events = row[date_columns].dropna().sort_values()
        for i in range(len(events) - 1):
            source, target = events.index[i], events.index[i + 1]
            duration = (events.iloc[i + 1] - events.iloc[i]).total_seconds() / (24 * 3600)
            if graph.has_edge(source, target):
                graph[source][target]['weight'] += 1
                graph[source][target]['durations'].append(duration)
            else:
                graph.add_edge(source, target, weight=1, durations=[duration])

    # Calculate mean durations
    for source, target, attr in graph.edges(data=True):
        attr['mean_duration'] = sum(attr['durations']) / len(attr['durations'])

    return graph


# Create PyVis Network
def add_to_network(net, graph):
    # Sort nodes by chronological appearance in the data
    # node_order = ['DT_ORDER_PLACED', 'DT_REGISTRATION_COMPLETED', 'DT_ORDER_DELIVERED', 'DT_TRANSPORT_REQUESTED',
    #               'DT_TRANSPORT_COMPLETED']
    # levels = {node: i for i, node in enumerate(node_order)}
    sorted_nodes = sorted(graph.nodes, key=lambda n: date_columns.index(n) if n in date_columns else len(date_columns))
    for i, node in enumerate(sorted_nodes):
        net.add_node(node, label=f"{node}", shape="box", color="lightblue", level=i, font={"size": 20})

    # Add edges sorted by weight
    sorted_edges = sorted(graph.edges(data=True), key=lambda e: e[2]['weight'], reverse=True)
    for source, target, attr in sorted_edges:
        if attr['weight'] > 1:
            duration = int(attr['mean_duration'])
            net.add_edge(
                source, target,
                label=f"{duration} days {attr['weight']} events",
                font={"size": 20, "align": "top"},
                smooth={"type": "curvedCW"},
                arrows={"to": {"enabled": True, "scaleFactor": 1.2}}
            )


# Generate HTML with Vehicle Type Filter
def generate_html(graph, vehicle_types):
    net = Network(height="800px", width="100%", directed=True, cdn_resources="in_line")

    # Add nodes and edges to the network
    add_to_network(net, graph)

    # Explicitly set hierarchical layout
    net.set_options("""
    var options = {
        "layout": {
            "hierarchical": {
                "enabled": true,
                "direction": "UD",
                "sortMethod": "directed",
                "nodeSpacing": 700,
                "levelSeparation": 300,
                "treeSpacing": 300
            }
        },
        "physics": {
            "enabled": false
        },
        "edges": {
            "smooth": {
                "enabled": true,
                "type": "cubicBezier",
                "forceDirection": "vertical"
            }
        }
    }
    """)

    # Add a filter for vehicle type
    vehicle_filter = """
    <script type="text/javascript">
    const allData = {
        nodes: {{ nodes|tojson }},
        edges: {{ edges|tojson }}
    };

    console.log("Initial Data:", allData);

    function filterGraph(vehicleType) {
        let filteredData = { nodes: [], edges: [] };

        if (vehicleType === 'All') {
            filteredData = allData;
        } else {
            filteredData.nodes = allData.nodes.filter(node => node.vehicle_type === vehicleType);
            const nodeIds = filteredData.nodes.map(node => node.id);
            filteredData.edges = allData.edges.filter(
                edge => nodeIds.includes(edge.from) && nodeIds.includes(edge.to)
            );
        }

        console.log("Filtered Nodes:", filteredData.nodes);
        console.log("Filtered Edges:", filteredData.edges);

        drawGraph(filteredData);
    }

    function drawGraph(data) {
        const container = document.getElementById("network");
        const networkData = {
            nodes: new vis.DataSet(data.nodes),
            edges: new vis.DataSet(data.edges),
        };
        const options = {
            layout: {
                hierarchical: {
                    enabled: true,
                    direction: "UD",
                    sortMethod: "directed",
                }
            },
            edges: {
                smooth: true,
                arrows: { to: { enabled: true } },
            },
            physics: false,
        };
        new vis.Network(container, networkData, options);
    }

    document.querySelectorAll('input[name="vehicleType"]').forEach(radio => {
        radio.addEventListener('change', (event) => {
            filterGraph(event.target.value);
        });
    });

    filterGraph('All');
</script>
"""

    # Generate the PyVis HTML and inject the vehicle filter
    html = net.generate_html()
    html = html.replace('<body>', f'<body>{vehicle_filter}', 1)

    # Write to an HTML file
    with open('fleet_maintenance_process.html', 'w') as f:
        f.write(html)


# Main logic
vehicle_type = 'All'  # Change dynamically based on user input in the HTML filter
graph = build_graph(data, vehicle_type)
generate_html(graph, vehicle_types)


