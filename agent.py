# agent.py
import heapq
import math
import random
from collections import deque

MOVES = {'Up': (0, 1), 'Down': (0, -1), 'Left': (-1, 0), 'Right': (1, 0)}
MOVE_ORDER = ['Up', 'Right', 'Down', 'Left'] 


class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        pos = percept['agent_pos']
        return random.choice(self.actions_pool)


# ===================Practical 02 - Step 1.2: Simple Reflex Agent=============================
class SimpleReflexAgent:
    """Strict IF-THEN (Condition-Action) rules on the CURRENT percept only.

    There is deliberately no __init__ and no attributes: the agent has zero memory.
    """

    def sense_and_act(self, percept: dict) -> str:
                    # Rule 1: IF food_here THEN Suck
        if percept.get('food_here'):
            return 'Suck'
                    # Rule 2: IF wall_ahead THEN Left 
        if percept.get('wall_ahead'):
            return 'Left'
                    # Rule 3: ELSE Right (keep heading right)
        return 'Right'


# ========================= Practical 02 - Step 1.3: Model-Based Agent =============================
class ModelBasedAgent:
    """Reflex agent with an internal state (a model of the world it cannot see)."""

    def __init__(self):
        self.x, self.y = 0, 0              
        self.facing = 'Right'                
        self.visited = {(0, 0): 1}           
        self.blocked = {}                     
        self.toxic = set()                    
        self.last_action = None

    # State update: runs FIRST on every step 
    def update_state(self, percept: dict):
        if self.last_action in MOVES:
            self.facing = self.last_action
            if not percept.get('bumped', False):
                dx, dy = MOVES[self.last_action]
                self.x += dx
                self.y += dy
                cell = (self.x, self.y)
                self.visited[cell] = self.visited.get(cell, 0) + 1

        here = (self.x, self.y)

        if percept.get('wall_ahead'):
            self.blocked.setdefault(here, set()).add(self.facing)
        if percept.get('smells_toxin'):
            self.toxic.add(here)

    # Condition-Action rules that query the memory 
    def sense_and_act(self, percept: dict) -> str:
        self.update_state(percept)
        here = (self.x, self.y)

                    # Rule 1: IF food_here THEN Suck
        if percept.get('food_here'):
            action = 'Suck'
        else:
            action = self._choose_direction(here)

        self.last_action = action
        return action

    def _choose_direction(self, here) -> str:
        blocked_here = self.blocked.get(here, set())
        best, best_key = None, None

        for index, direction in enumerate(MOVE_ORDER):
                        # Rule 2: IF that direction is known to be blocked THEN never choose it again
            if direction in blocked_here:
                continue

            dx, dy = MOVES[direction]
            neighbour = (here[0] + dx, here[1] + dy)

                        # Rule 3: IF the neighbour is a known toxic cell THEN avoid it (big penalty)
                        # Rule 4
            visits = self.visited.get(neighbour, 0) + (100 if neighbour in self.toxic else 0)
            keep_straight = 0 if direction == self.facing else 1
            key = (visits, keep_straight, index)

            if best_key is None or key < best_key:
                best, best_key = direction, key

        # Boxed in on all sides
        return best if best is not None else 'Suck'


# ============================= Practical 03 placeholder ========================================
class SearchAgent:
    """Goal-based agent: plans a whole path offline with BFS, DFS or UCS, then executes it."""

    def __init__(self, active_algo='BFS', heuristic_type='manhattan'):
        self.plan = []                   
        self.active_algo = active_algo   
        self.heuristic_type = heuristic_type  
        self.last_expanded = 0            

    # Step 1.1: heuristic functions 
    def manhattan_distance(self, pos, goal):
        """h(n) = |x1 - x2| + |y1 - y2|"""
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def euclidean_distance(self, pos, goal):
        """h(n) = sqrt((x1 - x2)^2 + (y1 - y2)^2)"""
        return math.sqrt((pos[0] - goal[0]) ** 2 + (pos[1] - goal[1]) ** 2)

    # State space: successors of a cell
    def _successors(self, state, walls, grid_size):
        width, height = grid_size
        for action in MOVE_ORDER:
            dx, dy = MOVES[action]
            nxt = (state[0] + dx, state[1] + dy)
            if 0 <= nxt[0] < width and 0 <= nxt[1] < height and nxt not in walls:
                yield action, nxt

    # BFS: FIFO queue (deque.popleft) 
    def bfs_search(self, start_pos, goal_pos, walls, grid_size):
        start, goal, walls = tuple(start_pos), tuple(goal_pos), {tuple(w) for w in walls}
        frontier = deque([(start, [])])
        reached = {start}
        self.last_expanded = 0
        while frontier:
            state, path = frontier.popleft()         
            self.last_expanded += 1
            if state == goal:
                return path
            for action, nxt in self._successors(state, walls, grid_size):
                if nxt not in reached:
                    reached.add(nxt)
                    frontier.append((nxt, path + [action]))
        return None                                   # goal unreachable

    # DFS: LIFO stack (list.pop) 
    def dfs_search(self, start_pos, goal_pos, walls, grid_size):
        start, goal, walls = tuple(start_pos), tuple(goal_pos), {tuple(w) for w in walls}
        frontier = [(start, [])]
        reached = set()
        self.last_expanded = 0
        while frontier:
            state, path = frontier.pop()             
            if state in reached:
                continue
            reached.add(state)
            self.last_expanded += 1
            if state == goal:
                return path
            for action, nxt in self._successors(state, walls, grid_size):
                if nxt not in reached:
                    frontier.append((nxt, path + [action]))
        return None

    # UCS: priority queue ordered by path cost g(n) 
    def ucs_search(self, start_pos, goal_pos, walls, grid_size):
        start, goal, walls = tuple(start_pos), tuple(goal_pos), {tuple(w) for w in walls}
        counter = 0                                 
        frontier = [(0, counter, start, [])]
        reached = {start: 0}                       
        self.last_expanded = 0
        while frontier:
            g, _, state, path = heapq.heappop(frontier)  
            if g > reached.get(state, float('inf')):
                continue                             
            self.last_expanded += 1
            if state == goal:
                return path
            for action, nxt in self._successors(state, walls, grid_size):
                new_g = g + 1                        
                if new_g < reached.get(nxt, float('inf')):
                    reached[nxt] = new_g
                    counter += 1
                    heapq.heappush(frontier, (new_g, counter, nxt, path + [action]))
        return None

    # Step 1.2: A* search, f(n) = g(n) + h(n) 
    def astar_search(self, start_pos, goal_pos, walls, grid_size, heuristic_type='manhattan'):
        start, goal, walls = tuple(start_pos), tuple(goal_pos), {tuple(w) for w in walls}
        h = self.manhattan_distance if heuristic_type == 'manhattan' else self.euclidean_distance

        frontier = []                     
        reached_states = set()
        self.last_expanded = 0

        # tuple format: (f_cost, g_cost, current_pos, path_taken); for the start, g(n) = 0
        heapq.heappush(frontier, (0 + h(start, goal), 0, start, []))

        while frontier:
            f_cost, g_cost, current_pos, path_taken = heapq.heappop(frontier)  
            if current_pos in reached_states:
                continue               
            self.last_expanded += 1
            if current_pos == goal:
                return path_taken
            reached_states.add(current_pos)

            for action, nxt in self._successors(current_pos, walls, grid_size):
                if nxt in reached_states:
                    continue
                g_new = g_cost + 1       
                h_new = h(nxt, goal)
                f_new = g_new + h_new
                heapq.heappush(frontier, (f_new, g_new, nxt, path_taken + [action]))
        return None                      

    # Step 1.3: form a whole plan, then execute it step by step 
    def sense_and_act(self, percept: dict) -> str:
        if percept.get('bumped'):
            self.plan = []                        
        if not self.plan:                             
            # Step 1.3: choose the search that matches self.active_algo
            if self.active_algo == 'BFS':
                search = self.bfs_search
            elif self.active_algo == 'DFS':
                search = self.dfs_search
            elif self.active_algo == 'UCS':
                search = self.ucs_search
            elif self.active_algo == 'AStar':
                search = lambda s, g, w, gs: self.astar_search(s, g, w, gs, self.heuristic_type)
            else:
                raise ValueError(f"Unknown algorithm: {self.active_algo}")
            self.plan = self._make_plan(percept, search)

        if not self.plan:                             
            return 'Suck'
        return self.plan.pop(0)

    def _make_plan(self, percept: dict, search):
        pos = tuple(percept['agent_pos'])

        # closest food first
        foods = sorted(percept['all_food'], key=lambda f: abs(f[0] - pos[0]) + abs(f[1] - pos[1]))
        for goal in foods:
            path = search(pos, tuple(goal), percept['walls'], percept['grid_size'])
            if path is not None:
                print(f"[{self.active_algo}] {pos} -> {tuple(goal)}: "
                      f"{len(path)} moves, {self.last_expanded} nodes expanded")
                return path + ['Suck']               
        return []


if __name__ == "__main__":
    # Step 1.1 testing checkpoint: start (0, 0), goal (3, 4)
    checker = SearchAgent()
    print("Manhattan:", checker.manhattan_distance((0, 0), (3, 4)))   
    print("Euclidean:", checker.euclidean_distance((0, 0), (3, 4)))   