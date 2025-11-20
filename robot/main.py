import numpy as np
import matplotlib.pyplot as plt
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement


from PIL import Image

import numpy as np
from PIL import Image

def load_map_as_numpy(image_path: str) -> np.ndarray:
    img = Image.open(image_path).convert('L')      # 'L' = 8-bit grayscale
    array = np.array(img)                          # значения 0..255, где 0 = чёрный
    binary_map = (array > 50).astype(np.uint8)     # 50 — порог, можно подстроить
    # binary_map = np.flipud(binary_map)
    return binary_map

# ==================== Твоя карта ====================
map_array = load_map_as_numpy("../data/maps/map1.png")

# map_array = np.flipud(map_array)  # если нужно

grid = Grid(matrix=map_array.tolist())

# Точки A → B → C (подставь свои!)
start_node = grid.node(90, 350)   # A
mid_node   = grid.node(490, 200)   # B
end_node   = grid.node(150, 120)   # C

finder = AStarFinder(diagonal_movement=DiagonalMovement.never)

path1 = finder.find_path(start_node, mid_node, grid)[0]
path2 = finder.find_path(mid_node,   end_node, grid)[0]
full_path_nodes = path1 + path2[1:]   # список объектов Node

# ==================== РАБОЧИЕ функции для ТЕКУЩЕЙ версии библиотеки ====================
def is_walkable(x: int, y: int, grid: Grid) -> bool:
    """Проверка проходимости клетки в актуальной версии библиотеки"""
    if not (0 <= x < grid.width and 0 <= y < grid.height):
        return False
    # В новых версиях walkable хранится прямо в узле, получаем его так:
    return grid.node(x, y).walkable

def line_of_sight(x0: int, y0: int, x1: int, y1: int, grid: Grid) -> bool:
    """Bresenham + проверка всех клеток на линии"""
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        if not is_walkable(x0, y0, grid):
            return False                    # попали в стену
        if x0 == x1 and y0 == y1:
            return True                     # дошли до конца
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

def string_pulling(path_nodes, grid: Grid):
    """Минимизируем количество точек — только прямые отрезки"""
    if len(path_nodes) <= 2:
        return [(n.x, n.y) for n in path_nodes]

    waypoints = [(path_nodes[0].x, path_nodes[0].y)]
    i = 0
    while i < len(path_nodes) - 1:
        for j in range(len(path_nodes) - 1, i, -1):
            if line_of_sight(path_nodes[i].x, path_nodes[i].y,
                             path_nodes[j].x, path_nodes[j].y, grid):
                waypoints.append((path_nodes[j].x, path_nodes[j].y))
                i = j
                break
        else:
            # если прямой видимости нет даже до следующей — добавляем её
            i += 1
            waypoints.append((path_nodes[i].x, path_nodes[i].y))
    return waypoints

# ==================== Финальная траектория ====================
waypoints = string_pulling(full_path_nodes, grid)
print(f"Сырой путь: {len(full_path_nodes)} клеток")
print(f"После оптимизации: {len(waypoints)} прямых отрезков")
print("Waypoints:", waypoints)

# ==================== Визуализация ====================
plt.figure(figsize=(12, 10))
vis = map_array.astype(float).copy()
vis[vis == 0] = np.nan

plt.imshow(vis, cmap='binary', origin='lower')

raw_x, raw_y = zip(*[(n.x, n.y) for n in full_path_nodes])
wp_x,  wp_y  = zip(*waypoints)

plt.plot(raw_x, raw_y, 'y-', alpha=0.5, linewidth=1, label='A* сырой путь')
plt.plot(wp_x,  wp_y,  'r-o', linewidth=4, markersize=10, label='Прямые отрезки')

plt.plot(start_node.x, start_node.y, 'bs', markersize=15, label='A')
plt.plot(mid_node.x,   mid_node.y,   'gs', markersize=15, label='B')
plt.plot(end_node.x,   end_node.y,   'ms', markersize=15, label='C')

plt.legend()
# plt.grid(True)
plt.title("Готовая траектория из прямых отрезков")
plt.show()