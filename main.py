import pygame
import sys
import time
from astar import search_algorithm

# --- CONFIGURATION ---
GRID_SIZE = 20
CELL_SIZE = 35 
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE + 160 # Extra space for Financial Dashboard
FPS = 60 

# FINANCIAL SETTINGS
FUEL_PRICE = 0.50 # AED per block
SALIK_PRICE = 4.00 # AED per yellow gate

# COLORS
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GREEN = (0, 200, 100)   # Start
RED = (255, 60, 60)     # Goal
GRAY = (50, 50, 55)     # Walls
YELLOW = (255, 215, 0)  # SALIK GATES
BLUE = (0, 120, 255)    # Path
PURPLE = (100, 50, 200) # Visited Nodes
UI_BG = (30, 30, 35)

class CityGrid:
    def __init__(self):
        self.start = (2, 9)
        self.end = (17, 9)
        self.walls = set()
        self.salik_gates = set()
        self.path = []
        self.visited = [] 
        self.cost = 0
        self.time_taken = 0
        self.nodes_count = 0
        self.current_algo = "A*" 
        
        # Financial Stats
        self.trip_fuel_cost = 0
        self.trip_salik_cost = 0
        self.trip_total_cost = 0
        
        self.dragging_start = False
        self.dragging_end = False

    def update_path(self):
        results = search_algorithm(
            self.start, self.end, self.walls, self.salik_gates, GRID_SIZE, self.current_algo
        )
        self.path, self.cost, self.visited, self.time_taken, self.nodes_count = results
        self.calculate_financials()

    def calculate_financials(self):
        if not self.path:
            self.trip_fuel_cost = 0
            self.trip_salik_cost = 0
            self.trip_total_cost = 0
            return

        # 1. Fuel Cost
        distance = len(self.path)
        self.trip_fuel_cost = distance * FUEL_PRICE

        # 2. Salik Cost
        salik_hits = 0
        for node in self.path:
            if node in self.salik_gates:
                salik_hits += 1
        self.trip_salik_cost = salik_hits * SALIK_PRICE

        # 3. Total
        self.trip_total_cost = self.trip_fuel_cost + self.trip_salik_cost

    def animate_search(self, screen):
        self.path = []
        self.draw(screen) 
        pygame.display.update()
        
        # Draw visited nodes step-by-step (Bonus Visualization)
        for node in self.visited:
            if node == self.start or node == self.end: continue
            
            x, y = node
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, PURPLE, rect)
            pygame.draw.rect(screen, (40, 40, 40), rect, 1)
            pygame.display.update()
            
            delay = 0.005 if self.current_algo == "Dijkstra" else 0.02
            time.sleep(delay) 
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()

        self.update_path()

    def draw(self, screen):
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                color = BLACK 
                
                if (x, y) in self.visited: color = (40, 20, 60) 
                
                if (x, y) in self.walls: color = GRAY
                elif (x, y) in self.salik_gates: color = YELLOW 
                elif (x, y) == self.start: color = GREEN
                elif (x, y) == self.end: color = RED
                
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (40, 40, 40), rect, 1)

        if self.path:
            points = [(p[0]*CELL_SIZE+CELL_SIZE/2, p[1]*CELL_SIZE+CELL_SIZE/2) for p in self.path]
            if len(points) > 1:
                pygame.draw.lines(screen, BLUE, False, points, 5)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("MetroFlow: Smart Logistics Simulation")
    
    font = pygame.font.SysFont('Consolas', 16)
    header_font = pygame.font.SysFont('Arial', 20, bold=True)
    big_font = pygame.font.SysFont('Arial', 24, bold=True)
    
    clock = pygame.time.Clock()
    
    city = CityGrid()
    city.update_path()

    running = True
    while running:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: 
                    city.walls.clear()
                    city.salik_gates.clear()
                    city.update_path()
                elif event.key == pygame.K_1: 
                    city.current_algo = "A*"
                    city.update_path()
                elif event.key == pygame.K_2: 
                    city.current_algo = "Dijkstra"
                    city.update_path()
                elif event.key == pygame.K_a: 
                    city.animate_search(screen)

            # MOUSE CONTROLS (User Interaction Bonus)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if pos[1] < GRID_SIZE * CELL_SIZE:
                    col, row = pos[0] // CELL_SIZE, pos[1] // CELL_SIZE
                    
                    if event.button == 1: # Left Click
                        if (col, row) == city.start: city.dragging_start = True
                        elif (col, row) == city.end: city.dragging_end = True
                        else:
                            city.walls.add((col, row)) # WALL
                            if (col, row) in city.salik_gates: city.salik_gates.remove((col, row))
                            city.update_path()
                            
                    elif event.button == 3: # Right Click
                        city.salik_gates.add((col, row)) # SALIK GATE
                        if (col, row) in city.walls: city.walls.remove((col, row))
                        city.update_path()

            elif event.type == pygame.MOUSEBUTTONUP:
                city.dragging_start = False
                city.dragging_end = False
            
            elif event.type == pygame.MOUSEMOTION:
                if city.dragging_start or city.dragging_end:
                    pos = pygame.mouse.get_pos()
                    if pos[1] < GRID_SIZE * CELL_SIZE:
                        col, row = pos[0] // CELL_SIZE, pos[1] // CELL_SIZE
                        if (col, row) not in city.walls and (col, row) != city.start and (col, row) != city.end:
                            if city.dragging_start: city.start = (col, row)
                            if city.dragging_end: city.end = (col, row)
                            city.update_path()

        city.draw(screen)

        # --- FINANCIAL DASHBOARD ---
        pygame.draw.rect(screen, UI_BG, (0, HEIGHT-160, WIDTH, 160))
        
        # Column 1: Algo Stats
        screen.blit(header_font.render("ALGORITHM", True, WHITE), (20, HEIGHT - 150))
        screen.blit(font.render(f"Type: {city.current_algo}", True, BLUE), (20, HEIGHT - 120))
        screen.blit(font.render(f"Time: {city.time_taken:.2f} ms", True, YELLOW), (20, HEIGHT - 100))
        screen.blit(font.render(f"Nodes: {city.nodes_count}", True, YELLOW), (20, HEIGHT - 80))

        # Column 2: Trip Costs (The "Business" Part)
        screen.blit(header_font.render("LOGISTICS COST (AED)", True, WHITE), (250, HEIGHT - 150))
        screen.blit(font.render(f"Fuel ({len(city.path)}km @ 0.5):", True, WHITE), (250, HEIGHT - 120))
        screen.blit(font.render(f"{city.trip_fuel_cost:.2f} AED", True, GREEN), (450, HEIGHT - 120))
        
        salik_count = int(city.trip_salik_cost / SALIK_PRICE)
        screen.blit(font.render(f"Salik ({salik_count} Gates @ 4.0):", True, WHITE), (250, HEIGHT - 100))
        screen.blit(font.render(f"{city.trip_salik_cost:.2f} AED", True, YELLOW if salik_count > 0 else GREEN), (450, HEIGHT - 100))
        
        screen.blit(big_font.render("TOTAL:", True, WHITE), (250, HEIGHT - 60))
        screen.blit(big_font.render(f"{city.trip_total_cost:.2f} AED", True, RED), (450, HEIGHT - 60))

        # Column 3: Instructions
        screen.blit(font.render("[L-Click] Wall", True, GRAY), (550, HEIGHT - 140))
        screen.blit(font.render("[R-Click] Salik Gate (4 AED)", True, YELLOW), (550, HEIGHT - 120))
        screen.blit(font.render("[A] Animate Search", True, BLUE), (550, HEIGHT - 100))
        screen.blit(font.render("[1/2] Switch Algo", True, BLUE), (550, HEIGHT - 80))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()