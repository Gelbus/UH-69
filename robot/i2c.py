import smbus2
import time
import struct

class I2C:
    def __init__(self):
        self.bus = smbus2.SMBus(1)

        # Адреса плат
        self.plate1 = 0x01
        self.plate2 = 0x02
        self.plate3 = 0x03

        # Флаг состояния
        self.is_completed = True

        # Адреса прошлой платы и текущей платы с которыми работаем
        self.last_plate = None
        self.current_plate = None

        # Переменные данных
        self.mes_id = 0     # id сообщения
        self.mail_type = 0  # тип сообщения
        self.seg_id = 0     # id участки трассы
        self.data = 0    # команда


    def gen_message(self, mail_type, data):
        # Данные для платформы
        if mail_type == 0:  # отправляем команду едь прямо и положительное или отрицательное направление движения
            self.data = data
            self.current_plate = self.plate1

        elif mail_type == 1:  # отправляем угол на который надо повернуть
            self.data = data
            self.current_plate = self.plate1

        elif mail_type == 2:  # Стоп
            self.data = 0
            self.current_plate = self.plate1

        # Данные на голову
        elif mail_type == 3:  # отправляем угол на который надо повернуть

            self.data = data # тут команда gcode
            self.current_plate = self.plate2

        # Данные на тинтаклю
        elif mail_type == 4:  # Левая
            self.data = data
            self.current_plate = self.plate3

        elif mail_type == 5:  # вместе
            self.data = data
            self.current_plate = self.plate3

        elif mail_type == 6:  # правая
            self.data = data
            self.current_plate = self.plate3



    def send_command(self):
        packet = struct.pack('<BBBh',
                              self.mes_id,
                              self.mail_type,
                              self.seg_id,
                              self.data)
        
        self.bus.write_i2c_block_data(
            self.current_plate, 
            0, # первый байт, его нужно пропускать при приёме данных ардуиной
            list(packet)
            )

        self.last_plate = self.current_plate
        self.is_completed = False
        self.mes_id += 1

        print(f"Sent command: {self.data} on plate {self.current_plate}")


    # def get_feedback(self):
    #     """Получить расстояние от Arduino"""
    #     is_complete = bus.read_byte(last_plate)
    #
    #     return is_complete


if __name__ == "__main__":
    i2c = I2C()
    # Пример использования
    try:
        while True:
            # Отправить команду "вперёд"
            if i2c.is_completed:
                # message = i2c.gen_message(0, [(0, 0), (10, 0)])
                i2c.send_command()

            # Получить обратную связь
            # i2c.get_feedback()

    except KeyboardInterrupt:
        print("Exiting...")