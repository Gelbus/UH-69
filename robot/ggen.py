# tower_gcode.py
# Подходит для башни: Cartesian XYZ + вращение вокруг своей оси (A или B)

def move_to(x=None, y=None, z=None, a=None, speed=3000):
    """
    x, y, z — миллиметры (линейные оси)
    a     — градусы вращения башни вокруг своей оси (A-ось)
    speed — мм/мин (или единицы/мин для A)
    """
    cmd = "G1"
    if x is not None: cmd += f" X{x:.3f}"
    if y is not None: cmd += f" Y{y:.3f}"
    if z is not None: cmd += f" Z{z:.3f}"
    if a is not None: cmd += f" A{a:.3f}"
    cmd += f" F{speed}"
    return cmd

def home():
    return "G28 X Y Z A"   # или G28 по отдельности, как у тебя настроено

# Пример траектории
gcode = [
    "$H",                    # хоминг всех осей
    "G90",                   # абсолютные координаты
    "G21",                   # миллиметры
    move_to(z=50),           # поднять над столом
    move_to(x=1000, y=0, a=0),
    move_to(x=1000, y=-500, a=45, speed=4000),
    move_to(x=1200, y=-450, z=820, a=37, speed=2500),
    move_to(z=50),           # опустить обратно
    "M5",                    # выключить шпиндель/лазер/что там у тебя
]

print("\n".join(gcode))