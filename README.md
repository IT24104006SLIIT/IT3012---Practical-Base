# Practical 03 - Uninformed Search (BFS, DFS, UCS)

Run (from my project folder):

```
python visual_grid_game.py bfs
python visual_grid_game.py dfs
python visual_grid_game.py ucs
python -m unittest test_suite
```

## Files
- `agent.py`: SearchAgent with bfs_search, dfs_search, ucs_search
- `visual_grid_game.py`: environment and GUI (percept now includes grid_size, walls, all_food, agent_pos)
- `Lab03_Evidence/`: screenshots of each run

## Observations
- DFS: plans of 27 to 99 moves for food only a few cells away; it used all 400 steps and ate 7 of 15 food (score 35).
- BFS: ate all 15 food in 59 steps, score 285 (plans of about 3 moves).
- UCS: ate all 15 food in 87 steps, score 285 (plans of about 5 moves). It behaves like BFS because every move costs 1; the numbers differ only because each run uses a different random map.

## Lab 03 Documentation
- `Jananjana J.W.C-IT24104006_Practical_03.pdf` (answers to the lab sheet)
  
