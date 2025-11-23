# from server.astar import PathGenerator


class Platform:
    def __init__(self):
        self.x: int # Текущая позиция x
        self.y: int # Текущая позиция y
        self.yaw: float # Угол курса
        
        self.d_dist: int
        self.d_yaw: float

        self.start_target_way = []
        self.target_finish_way = []



    def setup(self, path, yaw=0):
        self.start_target_way = path[0]
        self.target_finish_way = path[1]

        self.x = self.start_target_way[0][0]
        self.y = self.start_target_way[0][1]
        self.yaw = yaw

    def calc_movement(self):
        pass
    
    def rotate_platform(self):
        pass
    
    def move_forward(self):
        pass



