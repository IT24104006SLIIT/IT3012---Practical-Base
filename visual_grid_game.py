# visual_grid_game.py
import random
import sys
import tkinter as tk

from agent import SimpleReflexAgent, ModelBasedAgent

# Direction -> (dx, dy). Up means y + 1
DIRECTIONS = {'Up': (0, 1), 'Down': (0, -1), 'Left': (-1, 0), 'Right': (1, 0)}


class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with support for configurable opponents and larger scales."""

    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, custom_walls=None, num_traps=3,
                 max_steps=60):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]  

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}

        self.food_positions = set()
        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            pos_tuple = (fx, fy)
            if pos_tuple != (0, 0) and pos_tuple not in self.walls:
                self.food_positions.add(pos_tuple)

        # Make adversarial opponents
        self.opponents = []
        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)
            op_pos = [ox, oy]
            if tuple(op_pos) != (0, 0) and tuple(op_pos) not in self.walls and tuple(op_pos) not in self.food_positions:
                self.opponents.append(op_pos)

        # Step 2.1: hidden toxic traps (avoid start (0, 0), walls and food)
        self.toxic_traps = set()
        while len(self.toxic_traps) < num_traps:
            trap = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
            if trap != (0, 0) and trap not in self.walls and trap not in self.food_positions:
                self.toxic_traps.add(trap)

        self.score = 0
        self.steps = 0
        self.collision = False
        self.max_steps = max_steps

        # Practical 02: the agent now has a facing direction (the direction of its last move)
        self.facing = 'Right'
        self.bumped = False  # True if the agent's last move was blocked

    def _cell_ahead(self):
        """The adjacent cell in the agent's current facing direction."""
        dx, dy = DIRECTIONS[self.facing]
        return (self.agent_pos[0] + dx, self.agent_pos[1] + dy)

    def _is_blocked(self, cell) -> bool:
        """A cell is blocked if it is a wall or lies outside the grid."""
        x, y = cell
        return not (0 <= x < self.width and 0 <= y < self.height) or cell in self.walls

    # Step 1.1: partially observable percept 
    def get_percept(self) -> dict:
        """Local booleans only: no agent_pos, no opponent positions, no score."""
        return {
            'wall_ahead': self._is_blocked(self._cell_ahead()),
            'food_here': tuple(self.agent_pos) in self.food_positions,
            'smells_toxin': tuple(self.agent_pos) in self.toxic_traps,
            'bumped': self.bumped,
        }

    def execute_action(self, action: str):
        self.steps += 1
        self.bumped = False

        if action in DIRECTIONS:
            self.facing = action            # the agent faces the direction it tries to move
            target = self._cell_ahead()
            if self._is_blocked(target):
                self.bumped = True
                self.score -= 5             # bumping into a wall / the grid edge
            else:
                self.agent_pos = list(target)
                if target in self.toxic_traps:
                    self.score -= 15  # stepped onto a toxic trap
        elif action == 'Suck':
            here = tuple(self.agent_pos)
            if here in self.food_positions:
                self.food_positions.remove(here)
                self.score += 20

        for op in self.opponents:
            move = random.choice(['Up', 'Down', 'Left', 'Right', 'Stay'])
            if move == 'Up' and op[1] < self.height - 1:
                op[1] += 1
            elif move == 'Down' and op[1] > 0:
                op[1] -= 1
            elif move == 'Left' and op[0] > 0:
                op[0] -= 1
            elif move == 'Right' and op[0] < self.width - 1:
                op[0] += 1

            if op == self.agent_pos:
                self.score -= 50
                self.collision = True

    def is_done(self) -> bool:
        return len(self.food_positions) == 0 or self.steps >= self.max_steps or self.collision


class GridGameGUI:
    """Tkinter wrapper that dynamically scales cell sizes to keep larger grids on screen."""

    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=2, walls=None, agent=None,
                 max_steps=60):
        self.root = root
        self.root.title("IT3012 - Scalable Multi-Agent Grid Hunt")

        self.env = VisualGridHuntGame(width=width, height=height, num_food=num_food, num_opponents=num_opponents,
                                      custom_walls=walls, max_steps=max_steps)
        self.agent = agent if agent is not None else SimpleReflexAgent()

        max_canvas_dim = 600
        self.cell_size = max(20, min(max_canvas_dim // self.env.width, max_canvas_dim // self.env.height))

        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white")
        self.canvas.pack()

        self.label = tk.Label(root, text="Score: 0 | Steps: 0", font=("Arial", 14))
        self.label.pack(pady=10)

        self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop, font=("Arial", 12), bg="#000066",
                             fg="white")
        self.btn.pack(pady=5)

        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")

        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size
                y1 = (self.env.height - 1 - y) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = "#f1f5f9" if (x, y) not in self.env.walls else "#64748b"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#cbd5e1")

                if self.cell_size >= 40 and (x, y) in self.env.walls:
                    self.canvas.create_text(x1 + self.cell_size / 2, y1 + self.cell_size / 2, text="W", fill="white",
                                            font=("Arial", 8, "bold"))

        # Step 2.3: draw toxic traps as purple diamonds (visible to us, hidden from the agent)
        for tx, ty in self.env.toxic_traps:
            cs = self.cell_size
            x1 = tx * cs
            y1 = (self.env.height - 1 - ty) * cs
            self.canvas.create_polygon(x1 + cs * 0.5, y1 + cs * 0.15,
                                       x1 + cs * 0.85, y1 + cs * 0.5,
                                       x1 + cs * 0.5, y1 + cs * 0.85,
                                       x1 + cs * 0.15, y1 + cs * 0.5,
                                       fill="#7e22ce", outline="#581c87")

        for fx, fy in self.env.food_positions:
            offset = self.cell_size * 0.25
            x1 = fx * self.cell_size + offset
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset
            self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#f59e0b",
                                    outline="#d97706")

        for ox, oy in self.env.opponents:
            offset = self.cell_size * 0.2
            x1 = ox * self.cell_size + offset
            y1 = (self.env.height - 1 - oy) * self.cell_size + offset
            self.canvas.create_rectangle(x1, y1, x1 + self.cell_size * 0.6, y1 + self.cell_size * 0.6, fill="#990000",
                                         outline="#7a0000")

        ax, ay = self.env.agent_pos
        offset = self.cell_size * 0.15
        x1 = ax * self.cell_size + offset
        y1 = (self.env.height - 1 - ay) * self.cell_size + offset
        self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.7, y1 + self.cell_size * 0.7, fill="#000066",
                                outline="#1e3a8a")

        # Small white dot on the agent showing which way it is facing
        dx, dy = DIRECTIONS[self.env.facing]
        cx = x1 + self.cell_size * 0.35
        cy = y1 + self.cell_size * 0.35
        nx = cx + dx * self.cell_size * 0.22
        ny = cy - dy * self.cell_size * 0.22  
        r = self.cell_size * 0.07
        self.canvas.create_oval(nx - r, ny - r, nx + r, ny + r, fill="white", outline="")

    def run_loop(self):
        self.btn.config(state="disabled")

        def step():
            if not self.env.is_done():
                percept = self.env.get_percept()
                action = self.agent.sense_and_act(percept)
                self.env.execute_action(action)

                self.draw_grid()
                self.label.config(text=f"Score: {self.env.score} | Steps: {self.env.steps} | Action: {action} | Facing: {self.env.facing}")
                self.root.after(1000, step)
            else:
                end_text = f"Collision! Game Over! Final Score: {self.env.score}" if self.env.collision else f"Finished! Final Score: {self.env.score}"
                self.label.config(text=end_text)
                self.btn.config(state="normal")

        step()


if __name__ == "__main__":
    # Usage:  python visual_grid_game.py simple   (Step 1.2: Simple Reflex Agent, the default)
    #         python visual_grid_game.py model    (Step 1.3: Model-Based Agent)
    choice = sys.argv[1].lower() if len(sys.argv) > 1 else "simple"
    agent = ModelBasedAgent() if choice.startswith("model") else SimpleReflexAgent()

    root = tk.Tk()
    root.title(f"IT3012 - {type(agent).__name__}")
    app = GridGameGUI(root, width=12, height=12, num_food=15, num_opponents=0, agent=agent, max_steps=150)
    root.mainloop()