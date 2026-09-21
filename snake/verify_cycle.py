# -*- coding: utf-8 -*-
"""验证汉密尔顿回路：覆盖全部 400 格，蛇沿环走永不撞自己"""
COLS = ROWS = 22
N = COLS - 2  # 20

cycle = {}
def lk(a, b):
    cycle[(a[0], a[1])] = b

# y=1: left to right
for x in range(2, N+1):
    lk((x-1, 1), (x, 1))
lk((N, 1), (N, 2))

# y=2..19: zigzag
for y in range(2, N):
    if y % 2 == 0:
        for x in range(N, 2, -1):
            lk((x, y), (x-1, y))
        lk((2, y), (2, y+1))
    else:
        for x in range(3, N+1):
            lk((x-1, y), (x, y))
        lk((N, y), (N, y+1))

# y=20: right to left
for x in range(N, 1, -1):
    lk((x, N), (x-1, N))

# return column
for y in range(N-1, 1, -1):
    lk((1, y+1), (1, y))
lk((1, 2), (1, 1))

# Check: all 400 cells are keys
all_cells = set()
for y in range(1, N+1):
    for x in range(1, N+1):
        all_cells.add((x, y))
keys = set(cycle.keys())
print(f"cycle entries: {len(keys)}, expected 400")
missing = all_cells - keys
extra = keys - all_cells
if missing: print(f"MISSING: {missing}")
if extra: print(f"EXTRA: {extra}")
if not missing and not extra:
    print("COVERAGE: OK (all 400 cells)")

# Check: every cell maps to a valid adjacent cell
bad = []
for k, v in cycle.items():
    dx, dy = v[0]-k[0], v[1]-k[1]
    if abs(dx)+abs(dy) != 1:
        bad.append((k, v))
if bad:
    print(f"BAD EDGES: {bad[:5]}")
else:
    print("EDGES: OK (all adjacent)")

# Simulate snake following cycle
import random
random.seed(42)
snake = [(3,1), (2,1), (1,1)]  # head first
foods_eaten = 0
total_steps = 0
max_steps = 50000

# Place initial food
occupied = set(snake)
empty = [(x,y) for y in range(1,N+1) for x in range(1,N+1) if (x,y) not in occupied]
food_pos = random.choice(empty) if empty else None

while total_steps < max_steps:
    h = snake[0]
    nxt = cycle.get(h)
    if not nxt:
        print(f"ERROR: no cycle entry for {h}")
        break

    # Check collision with body (excluding tail, since tail moves when not eating)
    # But our game checks ALL segments. When board is full, this causes death.
    ate = False
    if food_pos and nxt == food_pos:
        ate = True
        foods_eaten += 1
        # place new food
        occupied = set(snake)
        empty = [(x,y) for y in range(1,N+1) for x in range(1,N+1) if (x,y) not in occupied]
        if empty:
            food_pos = random.choice(empty)
        else:
            food_pos = None  # board full
    else:
        snake.pop()  # tail moves

    # Check collision against remaining body
    if nxt in snake:
        print(f"COLLISION at step {total_steps}: head={nxt}, body_len={len(snake)}")
        break

    snake.insert(0, nxt)
    total_steps += 1

    if len(snake) == 400:
        print(f"BOARD FULL at step {total_steps}, snake length={len(snake)}, foods eaten={foods_eaten}")
        break

print(f"Final: steps={total_steps}, snake_len={len(snake)}, foods_eaten={foods_eaten}")
if len(snake) == 400:
    print("SUCCESS: snake filled the entire board!")
