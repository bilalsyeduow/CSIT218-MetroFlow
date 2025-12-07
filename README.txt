================================================================
METROFLOW - AI PROJECT SETUP GUIDE
================================================================

PROJECT: Intelligent Pathfinding (Topic 8)
TEAM: [Insert Your Names Here]

This folder contains the source code for "MetroFlow," an AI logistics 
simulation comparing A* and Dijkstra algorithms.

--- 1. FOLDER STRUCTURE ---
metroflow/
│
├── astar.py        # CORE LOGIC: Contains the A* and Dijkstra algorithms.
├── main.py         # SIMULATION: Pygame grid for visualization.
├── final_app.py    # REAL WORLD: Streamlit dashboard for Dubai map.
└── README.txt      # This file.

--- 2. INSTALLATION ---
To run this project, you need Python installed. 
Open your terminal (PowerShell or Command Prompt) and run:

pip install pygame streamlit streamlit-folium folium osmnx networkx pandas

(Note: If 'osmnx' gives an error, try updating pip: python -m pip install --upgrade pip)

--- 3. HOW TO RUN THE SIMULATION (GRID) ---
Use this to demonstrate the "Search Process" and "Drag-and-Drop".

1. Open Terminal inside the folder.
2. Run command:  python main.py

Controls:
- '1': Switch to A* (Fast).
- '2': Switch to Dijkstra (Thorough).
- 'A': Animate the search step-by-step.
- Left Click: Draw Walls.
- Right Click: Draw Traffic/Salik Gates.
- Spacebar: Reset.

--- 4. HOW TO RUN THE REAL-WORLD DASHBOARD ---
Use this to demonstrate the "Comparison" and "Financial Trade-off".

1. Open Terminal inside the folder.
2. Run command:  streamlit run final_app.py

Controls:
- Use Sidebar to switch between "Algorithm Race" and "Logistics Trade-off".
- Select "Add Salik Gate" to click and place yellow tolls on the map.
- Click Start and End points to calculate the route.
and also, install
note: unzip this folder. Before you run anything, you MUST open your terminal and run this command to install the tools, or it won't work
pip install pygame streamlit streamlit-folium folium osmnx networkx pandas