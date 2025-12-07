import osmnx as ox
import networkx as nx
import folium

print("--- BONUS TASK: REAL WORLD MAP (LONG DISTANCE) ---")
print("Generating path from Dubai Mall to UOWD...")
print("Note: Since this is a long route (15km+), map download may take 30-60 seconds.")

# 1. SETUP: Define Coordinates
# Start: Dubai Mall (Grand Entrance)
start_loc = (25.1972, 55.2744)
# End: UOWD Campus
end_loc = (25.1020, 55.1640)

# 2. DOWNLOAD MAP (Smart Midpoint Strategy)
# To find a path between two far points, we find the middle spot and 
# download a circle big enough to cover both.
mid_lat = (start_loc[0] + end_loc[0]) / 2
mid_lon = (start_loc[1] + end_loc[1]) / 2

# We need a radius of about 15km (15000m) to cover the highway between them
print("Downloading Map Data for Sheikh Zayed Road area...")
G = ox.graph_from_point((mid_lat, mid_lon), dist=15000, network_type='drive')

# 3. PATHFINDING
print("Calculating Shortest Path...")
# Snap GPS to nearest street
start_node = ox.distance.nearest_nodes(G, start_loc[1], start_loc[0])
end_node = ox.distance.nearest_nodes(G, end_loc[1], end_loc[0])

# Calculate shortest path by LENGTH (Distance)
route = nx.shortest_path(G, start_node, end_node, weight='length')

# 4. VISUALIZATION
print("Drawing Map...")
# Center map on the midpoint
m = folium.Map(location=[mid_lat, mid_lon], zoom_start=12, tiles="cartodbpositron")

# Draw Route
route_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in route]
folium.PolyLine(route_coords, color="blue", weight=5, opacity=0.7).add_to(m)

# Add Markers
folium.Marker(start_loc, popup="Dubai Mall", icon=folium.Icon(color='green', icon='shopping-bag', prefix='fa')).add_to(m)
folium.Marker(end_loc, popup="UOWD", icon=folium.Icon(color='red', icon='graduation-cap', prefix='fa')).add_to(m)

# Save
output_file = "Bonus_Real_Map.html"
m.save(output_file)
print(f"DONE! Open '{output_file}' to see the highway route.")