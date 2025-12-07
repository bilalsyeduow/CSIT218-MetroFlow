import heapq
import time

class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0

    def __lt__(self, other):
        return self.f < other.f

def heuristic(current_pos, end_pos):
    # Manhattan distance for grid
    return abs(current_pos[0] - end_pos[0]) + abs(current_pos[1] - end_pos[1])

def get_neighbors(node, grid_size):
    (x, y) = node.position
    neighbors = []
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)] 
    for dx, dy in directions:
        new_x, new_y = x + dx, y + dy
        if 0 <= new_x < grid_size and 0 <= new_y < grid_size:
            neighbors.append((new_x, new_y))
    return neighbors

def search_algorithm(start_pos, end_pos, walls, salik_gates, grid_size, algo_type="A*"):
    start_time = time.perf_counter()
    
    start_node = Node(start_pos)
    end_node = Node(end_pos)
    
    open_list = []
    closed_set = set()      
    visited_history = [] # Tracks nodes for the "Step-by-step" Bonus
    
    heapq.heappush(open_list, start_node)
    g_costs = {start_pos: 0}
    
    while open_list:
        current_node = heapq.heappop(open_list)
        closed_set.add(current_node.position)
        visited_history.append(current_node.position) 
        
        # Goal Reached
        if current_node.position == end_node.position:
            execution_time = (time.perf_counter() - start_time) * 1000 
            path = []
            while current_node:
                path.append(current_node.position)
                current_node = current_node.parent
            # Return: Path, Cost, Visited Nodes, Time, Node Count
            return path[::-1], g_costs[end_node.position], visited_history, execution_time, len(visited_history)
        
        for neighbor_pos in get_neighbors(current_node, grid_size):
            if neighbor_pos in walls or neighbor_pos in closed_set:
                continue
            
            # --- COST LOGIC (Economic Factor) ---
            # Normal Road = 1
            # Salik Gate (Yellow) = 10 (AI avoids this unless necessary)
            move_cost = 10 if neighbor_pos in salik_gates else 1
            
            new_g = current_node.g + move_cost
            
            if neighbor_pos not in g_costs or new_g < g_costs[neighbor_pos]:
                g_costs[neighbor_pos] = new_g
                neighbor_node = Node(neighbor_pos, current_node)
                neighbor_node.g = new_g
                
                # ALGORITHM COMPARISON
                if algo_type == "A*":
                    neighbor_node.h = heuristic(neighbor_pos, end_pos)
                else:
                    neighbor_node.h = 0 # Dijkstra has no heuristic
                
                neighbor_node.f = neighbor_node.g + neighbor_node.h
                heapq.heappush(open_list, neighbor_node)
                
    return [], 0, visited_history, 0, len(visited_history)