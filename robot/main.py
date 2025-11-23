from  PlatformBlock import Platform
from web import RobotVideoServer

from threading import Thread


class UH:
    def __init__(self):
        self.platform = Platform()
        self.head = None
        self.taker = None

        self.server = RobotVideoServer(self.platform, port=5000)



        self.running = False
    
    
    def wait_init(self):
        server_thread = Thread(target=self.server.run, kwargs={'debug':False, 'use_reloader':False}, daemon=True)
        server_thread.start()
        count = 0
        while not self.platform.is_ready_for_work:
            print(f"Ожидание инициализации платформы... {count}")
            count += 1
            # Добавь таймаут, чтобы не висеть вечно
            import time
            time.sleep(0.5)

        if self.platform.is_ready_for_work:
            print("Платформа готова к работе!")
        else:
            print("Платформа не запустилась")

    def run(self):

        while self.running:
            self.platform.calc_movement()
        

if __name__ == "__main__":
    robot = UH()
    robot.wait_init()
    robot.run()