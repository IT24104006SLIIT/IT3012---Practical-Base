# agent.py
import random

MOVES = {'Up': (0, 1), 'Down': (0, -1), 'Left': (-1, 0), 'Right': (1, 0)}
MOVE_ORDER = ['Up', 'Right', 'Down', 'Left']

class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        pos = percept['agent_pos']
        return random.choice(self.actions_pool)

class SimpleReflexAgent:
    """Strict IF-THEN rules on the CURRENT percept only (no __init__, no memory)."""

    def sense_and_act(self, percept: dict) -> str:
        if percept.get('food_here'):       # Rule 1
            return 'Suck'
        if percept.get('wall_ahead'):      # Rule 2
            return 'Left'
        return 'Right'                     # Rule 3


class ModelBasedAgent:
    """Reflex agent with an internal state (a model of the world it cannot see)."""

    def __init__(self):
        self.x, self.y = 0, 0
        self.facing = 'Right'
        self.visited = {(0, 0): 1}
        self.blocked = {}
        self.toxic = set()
        self.last_action = None

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

    def sense_and_act(self, percept: dict) -> str:
        self.update_state(percept)
        here = (self.x, self.y)

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
            if direction in blocked_here:
                continue
            dx, dy = MOVES[direction]
            neighbour = (here[0] + dx, here[1] + dy)
            visits = self.visited.get(neighbour, 0) + (100 if neighbour in self.toxic else 0)
            keep_straight = 0 if direction == self.facing else 1
            key = (visits, keep_straight, index)
            if best_key is None or key < best_key:
                best, best_key = direction, key

        return best if best is not None else 'Suck'


class SearchAgent:
    """Placeholder for Practical 03 (test_suite.py imports it)."""

    def bfs_search(self, start_pos, goal_pos, walls, grid_size):
        raise NotImplementedError("bfs_search is part of Practical 03")