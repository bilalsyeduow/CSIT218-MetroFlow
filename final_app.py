import streamlit as st
import folium
from streamlit_folium import st_folium
import osmnx as ox
import networkx as nx
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="MetroFlow: Master Dashboard")

st.title("🚛 MetroFlow: Master Logistics Dashboard")
st.markdown("### Select a **Simulation Mode** in the sidebar to begin.")

# --- SESSION STATE ---
if "start_point" not in st.session_state: st.session_state["start_point"] = None
if "end_point" not in st.session_state: st.session_state["end_point"] = None
if "salik_gates" not in st.session_state: st.session_state["salik_gates"] = []

# --- SIDEBAR: MASTER CONTROLS ---
st.sidebar.header("🎛️ Simulation Mode")
app_mode = st.sidebar.radio("Choose Analysis Type:", 
    ["🧠 Algorithm Race (A* vs Dijkstra)", "💰 Logistics Trade-off (Salik Analysis)"])

st.sidebar.markdown("---")

# 1. CONTROLS FOR LOGISTICS MODE
if app_mode == "💰 Logistics Trade-off (Salik Analysis)":
    st.sidebar.header("🕹️ Interaction")
    # THIS IS THE CLICK SELECTOR YOU ASKED FOR
    interaction_mode = st.sidebar.radio("Clicking Map will:", ["Set Start/End Points", "Add Salik Gate (Toll)"])
    
    st.sidebar.header("💵 Economic Factors")
    salik_price = st.sidebar.number_input("Salik Price (AED)", value=4.0)
    fuel_price = st.sidebar.number_input("Fuel Price (AED/L)", value=3.0)
    efficiency = st.sidebar.number_input("Car Efficiency (Km/L)", value=10.0)
    hourly_wage = st.sidebar.number_input("Your Time Value (AED/hr)", value=60.0)

# 2. CONTROLS FOR RACE MODE
else:
    st.sidebar.info("👉 This mode compares calculation speed. Salik gates are ignored here.")
    interaction_mode = "Set Start/End Points"

st.sidebar.markdown("---")
if st.sidebar.button("❌ Reset All Points"):
    st.session_state["start_point"] = None
    st.session_state["end_point"] = None
    st.session_state["salik_gates"] = []
    st.rerun()

# --- HELPER FUNCTIONS ---
def get_route_stats(graph, route):
    """ Calculates real-world distance (km) and time (min) for a route """
    dist_m = 0
    time_s = 0
    for u, v in zip(route[:-1], route[1:]):
        edge = graph.edges[u, v, 0]
        dist_m += edge.get('length', 0)
        time_s += edge.get('travel_time', 0)
    return dist_m / 1000, time_s / 60 

def dist_heuristic(u, v):
    return ((G.nodes[u]['x'] - G.nodes[v]['x'])**2 + (G.nodes[u]['y'] - G.nodes[v]['y'])**2)**0.5

# --- MAP PREPARATION ---
m = folium.Map(location=[25.15, 55.25], zoom_start=11, tiles="cartodbpositron")

# Draw Start/End
if st.session_state["start_point"]:
    folium.Marker(st.session_state["start_point"], icon=folium.Icon(color="green", icon="play"), popup="Start").add_to(m)
if st.session_state["end_point"]:
    folium.Marker(st.session_state["end_point"], icon=folium.Icon(color="red", icon="flag"), popup="Finish").add_to(m)

# Draw User-Added Salik Gates (Visible in both modes, but logic applies to Logistics)
for gate in st.session_state["salik_gates"]:
    folium.CircleMarker(
        location=gate, radius=8, color="orange", fill=True, fill_color="yellow", popup="Custom Salik Gate"
    ).add_to(m)

# --- CAPTURE CLICKS ---
output = st_folium(m, width=1400, height=500)

if output["last_clicked"]:
    coords = (output["last_clicked"]["lat"], output["last_clicked"]["lng"])
    
    if interaction_mode == "Set Start/End Points":
        if not st.session_state["start_point"]:
            st.session_state["start_point"] = coords
            st.rerun()
        elif not st.session_state["end_point"]:
            st.session_state["end_point"] = coords
            st.rerun()
            
    elif interaction_mode == "Add Salik Gate (Toll)":
        st.session_state["salik_gates"].append(coords)
        st.success("💰 Salik Gate Added! The Green Route will now try to avoid this.")
        time.sleep(0.5) 
        st.rerun()

# --- MAIN ENGINE ---
if st.session_state["start_point"] and st.session_state["end_point"]:
    st.markdown("---")
    
    start = st.session_state["start_point"]
    end = st.session_state["end_point"]
    gates = st.session_state["salik_gates"]
    
    mid_lat = (start[0] + end[0]) / 2
    mid_lon = (start[1] + end[1]) / 2
    dist_deg = ((start[0]-end[0])**2 + (start[1]-end[1])**2)**0.5
    graph_dist = max(3000, dist_deg * 111000 / 1.5)
    
    # ---------------------------------------------------------
    # MODE 1: ALGORITHM RACE (A* vs Dijkstra)
    # ---------------------------------------------------------
    if app_mode == "🧠 Algorithm Race (A* vs Dijkstra)":
        st.header("🏁 Speed Test: Which Algorithm is Faster?")
        
        with st.spinner("Downloading Map & Racing..."):
            try:
                global G
                G = ox.graph_from_point((mid_lat, mid_lon), dist=graph_dist, network_type='drive')
                start_node = ox.distance.nearest_nodes(G, start[1], start[0])
                end_node = ox.distance.nearest_nodes(G, end[1], end[0])
                
                # 1. Run Dijkstra
                t0 = time.perf_counter()
                path_d = nx.shortest_path(G, start_node, end_node, weight='length')
                time_d = (time.perf_counter() - t0) * 1000
                
                # 2. Run A* Search
                t0 = time.perf_counter()
                path_a = nx.astar_path(G, start_node, end_node, heuristic=dist_heuristic, weight='length')
                time_a = (time.perf_counter() - t0) * 1000
                
                # Metrics
                col1, col2, col3 = st.columns(3)
                col1.metric("🏆 Winner", "A* Search" if time_a < time_d else "Tie")
                col2.metric("A* CPU Time", f"{time_a:.2f} ms")
                col3.metric("Dijkstra CPU Time", f"{time_d:.2f} ms")
                
                # Visuals
                m_res = folium.Map(location=[mid_lat, mid_lon], zoom_start=12)
                folium.PolyLine([(G.nodes[n]['y'], G.nodes[n]['x']) for n in path_d], color="red", weight=8, opacity=0.5, tooltip="Dijkstra").add_to(m_res)
                folium.PolyLine([(G.nodes[n]['y'], G.nodes[n]['x']) for n in path_a], color="blue", weight=3, opacity=1, tooltip="A* Search").add_to(m_res)
                
                folium.Marker(start, icon=folium.Icon(color="green")).add_to(m_res)
                folium.Marker(end, icon=folium.Icon(color="red")).add_to(m_res)
                st_folium(m_res, width=1400, height=500)
                
            except Exception as e: st.error(f"Error: {e}")

    # ---------------------------------------------------------
    # MODE 2: LOGISTICS TRADE-OFF (Salik Analysis)
    # ---------------------------------------------------------
    elif app_mode == "💰 Logistics Trade-off (Salik Analysis)":
        st.header("📊 Scenario Analysis: Pay Salik vs Avoid Salik")
        
        with st.spinner("Calculating Scenarios..."):
            try:
                G = ox.graph_from_point((mid_lat, mid_lon), dist=graph_dist, network_type='drive')
                G = ox.add_edge_speeds(G)
                G = ox.add_edge_travel_times(G)
                
                start_node = ox.distance.nearest_nodes(G, start[1], start[0])
                end_node = ox.distance.nearest_nodes(G, end[1], end[0])

                # --- ROUTE A: PAY SALIK (Fastest / Shortest) ---
                # This route ignores the yellow dots and goes straight through
                path_salik = nx.shortest_path(G, start_node, end_node, weight='travel_time')
                dist_salik, time_salik = get_route_stats(G, path_salik)
                
                # Did we actually hit the user's custom gates?
                salik_hits = 0
                if gates:
                    path_nodes = set(path_salik)
                    for gate in gates:
                        g_node = ox.distance.nearest_nodes(G, gate[1], gate[0])
                        # Check if path contains this node
                        if g_node in path_nodes: salik_hits += 1

                # --- ROUTE B: AVOID SALIK (Cheapest / Longest) ---
                # We modify the graph to make the yellow dots "impossible" to pass
                G_avoid = G.copy()
                if gates:
                    for gate in gates:
                        g_node = ox.distance.nearest_nodes(G_avoid, gate[1], gate[0])
                        # Add HUGE time penalty (1 hour) to edges connected to this node
                        for u, v, k, data in G_avoid.edges(keys=True, data=True):
                            if u == g_node or v == g_node:
                                data['travel_time'] += 3600 

                path_avoid = nx.shortest_path(G_avoid, start_node, end_node, weight='travel_time')
                dist_avoid, time_avoid_raw = get_route_stats(G, path_avoid) 

                # --- FINANCIALS (THE RULE OF THUMB) ---
                # Route A: Less Time, Less Fuel (usually), More Salik Cost
                cost_fuel_salik = dist_salik * (fuel_price / efficiency)
                total_cost_salik = cost_fuel_salik + (salik_hits * salik_price)

                # Route B: More Time, More Fuel (longer distance), 0 Salik Cost
                cost_fuel_avoid = dist_avoid * (fuel_price / efficiency)
                total_cost_avoid = cost_fuel_avoid
                
                # Differences
                money_saved = total_cost_salik - total_cost_avoid
                time_lost = time_avoid_raw - time_salik
                value_lost = (time_lost/60) * hourly_wage
                
                rec = "✅ **Recommendation: AVOID SALIK**" if money_saved > value_lost else "🚀 **Recommendation: PAY SALIK**"
                st.success(rec)

                col1, col2 = st.columns(2)
                with col1:
                    st.error(f"🔴 Route A: Pay Salik")
                    st.metric("Time", f"{time_salik:.0f} mins")
                    st.metric("Total Cost", f"{total_cost_salik:.2f} AED")
                    st.caption(f"Salik Hits: {salik_hits} | Fuel Cost: {cost_fuel_salik:.2f} AED")
                with col2:
                    st.success(f"🟢 Route B: Avoid Salik")
                    st.metric("Time", f"{time_avoid_raw:.0f} mins", f"+{time_lost:.0f} min slower", delta_color="inverse")
                    st.metric("Total Cost", f"{total_cost_avoid:.2f} AED", f"-{money_saved:.2f} AED saved")
                    st.caption(f"Salik Hits: 0 | Fuel Cost: {cost_fuel_avoid:.2f} AED")

                # Map Visuals
                m_res = folium.Map(location=[mid_lat, mid_lon], zoom_start=12)
                
                # Draw Red (Pay Salik)
                folium.PolyLine([(G.nodes[n]['y'], G.nodes[n]['x']) for n in path_salik], color="red", weight=6, opacity=0.5, tooltip="Pay Salik").add_to(m_res)
                
                # Draw Green (Avoid Salik)
                if path_avoid != path_salik:
                    folium.PolyLine([(G.nodes[n]['y'], G.nodes[n]['x']) for n in path_avoid], color="green", weight=4, opacity=0.9, tooltip="Avoid Salik").add_to(m_res)

                folium.Marker(start, icon=folium.Icon(color="green")).add_to(m_res)
                folium.Marker(end, icon=folium.Icon(color="red")).add_to(m_res)
                
                for gate in gates:
                     folium.CircleMarker(location=gate, radius=8, color="orange", fill=True, fill_color="yellow").add_to(m_res)

                st_folium(m_res, width=1400, height=500)
                
            except Exception as e: st.error(f"Analysis Failed: {e}")