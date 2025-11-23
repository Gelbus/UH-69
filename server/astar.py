from typing import List

import numpy as np
import matplotlib.pyplot as plt
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement
from PIL import Image
from scipy.ndimage import binary_dilation


class PathGenerator:
    def __init__(self,
                 start_p: tuple[int, int],
                 target_p: tuple[int, int],
                 finish_p: tuple[int, int],
                 impath: str = "../data/maps/map1.png"):

        self.start: tuple[int, int] = start_p
        self.target: tuple[int, int] = target_p
        self.finish: tuple[int, int] = finish_p

        self.start_node = None
        self.target_node = None
        self.finish_node = None

        self.cell_size_cm: int = 1  # Предполагаем, что 1 клетка = 1 см
        self.robot_size_cm: int = 50  # Размер робота 50 см

        self.impath: str = impath
        self.binary_map_arr = None
        self._dilated_map_arr = None


    # Загрузка png карты
    def _load_map_as_numpy(self) -> None:
        img = Image.open(self.impath).convert('L')  # 'L' = 8-bit grayscale
        array = np.array(img)  # значения 0..255, где 0 = чёрный
        # array = np.flipud(array)  # ← ПЕРЕВОРАЧИВАЕМ!
        self.binary_map_arr = (array > 50).astype(np.uint8)  # 50 — порог


    # Расширение препятствий на размер нашего робота
    def _dilate_map(self) -> None:
        dilation_radius = int(np.ceil(self.robot_size_cm / 2 / self.cell_size_cm))
        obstacle_map = 1 - self.binary_map_arr
        structure = np.ones((dilation_radius * 2 + 1, dilation_radius * 2 + 1), dtype=bool)
        dilated_obstacles = binary_dilation(obstacle_map, structure=structure)
        self._dilated_map_arr = 1 - dilated_obstacles.astype(np.uint8)


    # Упрощаем траекторию, чтобы были отрезки от поворота до поворота
    # def _simplify_path(self, points):
    #     if len(points) <= 2:
    #         return points.copy()
    #     simplified = [points[0]]  # первая точка всегда остаётся
    #     for i in range(1, len(points) - 1):
    #         prev = points[i - 1]
    #         curr = points[i]
    #         next_p = points[i + 1]
    #         # вектор от prev до curr
    #         vx1 = curr[0] - prev[0]
    #         vy1 = curr[1] - prev[1]
    #         # вектор от curr до next
    #         vx2 = next_p[0] - curr[0]
    #         vy2 = next_p[1] - curr[1]
    #         # если векторы коллинеарны (векторное произведение == 0) — точка промежуточная
    #         if vx1 * vy2 - vx2 * vy1 != 0:
    #             simplified.append(curr)
    #     simplified.append(points[-1])  # последняя точка всегда остаётся
    #     return simplified

    def _simplify_path(self, points):
        if len(points) < 3:
            return points[:]

        simplified = [points[0]]
        for i in range(1, len(points) - 1):
            x0, y0 = points[i - 1]
            x1, y1 = points[i]
            x2, y2 = points[i + 1]

            # Векторное произведение
            if (x1 - x0) * (y2 - y1) - (x2 - x1) * (y1 - y0) != 0:
                simplified.append(points[i])

        simplified.append(points[-1])
        return simplified

    def get_path(self) -> tuple[list[int], list[int]]:
        self._load_map_as_numpy()

        # Создаём карту с учётом размера робота
        self._dilate_map()

        # Создаём grid на основе модифицированной карты
        grid = Grid(matrix=self._dilated_map_arr.tolist())
        finder = AStarFinder(diagonal_movement=DiagonalMovement.never)

        # Точки A → B → C
        self.start_node = grid.node(*self.start)  # A Старт
        self.target_node = grid.node(*self.target)  # B Целевая точка
        self.finish_node = grid.node(*self.finish)  # C Точка выгрузки

        # Путь старт-цель
        path1 = finder.find_path(self.start_node, self.target_node, grid)[0]

        # Путь цель-финиш
        path2 = finder.find_path(self.target_node, self.finish_node, grid)[0]

        # full_path_nodes = path1 + path2[1:]  # список объектов Node
        #
        # path = [(n.x, n.y) for n in full_path_nodes]

        points1 = self._simplify_path([(n.x, n.y) for n in path1])
        points2 = self._simplify_path([(n.x, n.y) for n in path2])

        # print(points)
        #
        # raw_x: list[int]
        # raw_y: list[int]
        # raw_x,raw_y = zip(*points)

        return points1, points2


def draw(raw_x, raw_y, start, target, finish, map_array):
    # ==================== Визуализация (на оригинальной карте) ====================
    plt.figure(figsize=(12, 10))
    vis = map_array.astype(float).copy()  # Используем оригинальную карту для отображения
    vis[vis == 0] = np.nan

    plt.imshow(vis, cmap='binary', origin='lower')
    plt.plot(raw_x, raw_y, 'y-', alpha=0.5, linewidth=1, label='A* сырой путь')

    plt.plot(*start, 'bs', markersize=15, label='A')
    plt.plot(*target, 'gs', markersize=15, label='B')
    plt.plot(*finish, 'ms', markersize=15, label='C')

    plt.legend()
    plt.title("Готовая траектория с учётом размера робота")
    plt.show()

if __name__ == "__main__":
    start = (90, 360 - 350)
    target = (490, 360 - 200)
    finish = (150, 360 - 120)
    impath = "../data/maps/map1.png"

    path_generator = PathGenerator(start, target, finish, impath)

    raw_x, raw_y = path_generator.get_path()


    draw(raw_x, raw_y,
         path_generator.start,
         path_generator.target,
         path_generator.finish,
         path_generator.binary_map_arr)