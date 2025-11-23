from  platform_moving import Platform

import data_exchange


class UH:
    def __init__(self):
        self.platform = Platform()
        self.head = None
        self.taker = None

        self.running = True
    
    
    def wait_init(self):
        data_exchange.run_exchange(self.platform)
        # self.platform.setup()
    
    def run(self):

        while self.running:

            self.platform.calc_movement()
        

if __name__ == "__main__":
    robot = UH()
    robot.wait_init()
    robot.run()