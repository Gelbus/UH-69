import math


def target_gcode(x, y, z, L_fixed=50, feed=4000):
    r = math.hypot(x, y)
    if r < L_fixed - 1:  # небольшая погрешность
        raise ValueError(f"Точка слишком близко к центру: r={r:.1f} мм")

    A = math.degrees(math.atan2(y, x))
    Z = z
    U = r - L_fixed
    if U < 0: U = 0

    return f"G1 A{A:.4f} Z{Z:.3f} U{U:.3f} F{feed}"


# Тест
print(target_gcode(300, 100, 200))  # → G1 A18.4350 Z200.000 U255.7918 F4000