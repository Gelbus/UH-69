# from server.astar import PathGenerator


class Platform:
    def __init__(self):

        self.is_ready_for_work = False

        self.x: int # Текущая позиция x
        self.y: int # Текущая позиция y
        self.yaw: float # Угол курса
        
        self.d_dist: int
        self.d_yaw: float

        self.start_target_way = []
        self.target_finish_way = []

        self.start_target_dist = []
        self.target_finish_dist = []

        self.start_target_angles = []
        self.target_finish_angles = []

        self.command_list = []



    def setup(self, path, yaw=0):
        # Инициализация начальных координат
        self.command_list = []
        self.start_target_way = path[0]
        self.target_finish_way = path[1]

        self.x = self.start_target_way[0][0]
        self.y = self.start_target_way[0][1]
        self.yaw = yaw

        # Расчёт дистанций
        self.start_target_dist = [
            ((self.start_target_way[i][0] - self.start_target_way[i - 1][0]) ** 2 +
             (self.start_target_way[i][1] - self.start_target_way[i - 1][1]) ** 2) ** 0.5
            for i in range(1, len(self.start_target_way))]

        self.target_finish_dist = [
            ((self.target_finish_way[i][0] - self.target_finish_way[i - 1][0]) ** 2 +
             (self.target_finish_way[i][1] - self.target_finish_way[i - 1][1]) ** 2) ** 0.5
            for i in range(1, len(self.target_finish_way))]



        # Расчёт углов поворотов
        # north_vec = (0, -1) # единичный вектор, направленный на север, для расчёта угла поворота
        start_target_directions = [
            (
                (self.start_target_way[i][0] - self.start_target_way[i - 1][0]) / self.start_target_dist[i - 1],
                (self.start_target_way[i][1] - self.start_target_way[i - 1][1]) / self.start_target_dist[i - 1]
            )
            for i in range(1, len(self.start_target_way))
        ]
        target_finish_directions = [
            (
                (self.target_finish_way[i][0] - self.target_finish_way[i - 1][0]) / self.target_finish_dist[i - 1],
                (self.target_finish_way[i][1] - self.target_finish_way[i - 1][1]) / self.target_finish_dist[i - 1]
            )
            for i in range(1, len(self.target_finish_way))
        ]


        angle = 0

        for xy in start_target_directions:
            if xy[0] == 0 and xy[1] == -1: # На север
                angle = 0
            elif xy[0] == 1 and xy[1] == 0: # На восток
                angle = 90
            elif xy[0] == 0 and xy[1] == 1: # На юг
                angle = 180
            elif xy[0] == -1 and xy[1] == 0: # На запад
                angle = 270

            self.start_target_angles.append(angle)

        for xy in target_finish_directions:
            if xy[0] == 0 and xy[1] == -1:  # На север
                angle = 0
            elif xy[0] == 1 and xy[1] == 0:  # На восток
                angle = 90
            elif xy[0] == 0 and xy[1] == 1:  # На юг
                angle = 180
            elif xy[0] == -1 and xy[1] == 0:  # На запад
                angle = 270

            self.target_finish_angles.append(angle)


        # tmp_angle = self.yaw
        for i in range(len(self.start_target_angles) - 1, 1, -1):
            self.start_target_angles[i] -= self.start_target_angles[i - 1]
        self.start_target_angles[0] -= self.yaw

        # Тут вставить алгоритм поиска арукометки и пересчёта угла. Похорошему выровнять робота в север и тогда будет работать в общем случае

        for i in range(len(self.target_finish_angles) - 1, 0, -1):
            self.target_finish_angles[i] -= self.target_finish_angles[i - 1]
        self.target_finish_angles[0] -= self.yaw






        print(self.start_target_way)
        print(self.start_target_dist)
        print(start_target_directions)
        print(self.start_target_angles)

        print(self.target_finish_way)
        print(self.target_finish_dist)
        print(target_finish_directions)
        print(self.target_finish_angles)

        self.is_ready_for_work = True



    def calc_movement(self):
        pass
    
    def rotate_platform(self):
        pass
    
    def move_forward(self):
        pass



