import numpy as np
import cv2

# Словарь остался тем же
ARUCO_DICT = {
    "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
    "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
    # ... остальные можно оставить
}

def aruco_display(corners, ids, rejected, image):
    if len(corners) > 0:
        ids = ids.flatten()
        for (markerCorner, markerID) in zip(corners, ids):
            corners_array = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners_array.astype(int)

            cv2.line(image, topLeft, topRight, (0, 255, 0), 2)
            cv2.line(image, topRight, bottomRight, (0, 255, 0), 2)
            cv2.line(image, bottomRight, bottomLeft, (0, 255, 0), 2)
            cv2.line(image, bottomLeft, topLeft, (0, 255, 0), 2)

            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)
            cv2.circle(image, (cX, cY), 4, (0, 0, 255), -1)

            cv2.putText(image, str(markerID), (topLeft[0], topLeft[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            print(f"[Inference] ArUco marker ID: {markerID}")

    return image


def pose_estimation(frame, aruco_dict_type, matrix_coefficients, distortion_coefficients, marker_size=0.02):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = cv2.aruco.getPredefinedDictionary(aruco_dict_type)
    parameters = cv2.aruco.DetectorParameters()

    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
    corners, ids, rejected = detector.detectMarkers(gray)

    # Рисуем обнаруженные маркеры
    if ids is not None:
        frame = aruco_display(corners, ids, rejected, frame)

        # Подготовка 3D-точек маркера (в метрах, размер маркера = marker_size)
        obj_points = np.array([[-marker_size/2,  marker_size/2, 0],
                               [ marker_size/2,  marker_size/2, 0],
                               [ marker_size/2, -marker_size/2, 0],
                               [-marker_size/2, -marker_size/2, 0]], dtype=np.float32)

        for i in range(len(ids)):
            # 2D точки текущего маркера
            img_points = corners[i][0].astype(np.float32)

            # solvePnP вместо старого estimatePoseSingleMarkers
            success, rvec, tvec = cv2.solvePnP(obj_points, img_points,
                                               matrix_coefficients, distortion_coefficients)

            if success:
                # Рисуем оси
                cv2.drawFrameAxes(frame, matrix_coefficients, distortion_coefficients,
                                  rvec, tvec, length=0.03, thickness=3)

                # Можно вывести расстояние (длина tvec)
                distance = np.linalg.norm(tvec)
                print(f"Marker {ids[i][0]} distance: {distance:.3f} m")

    return frame


# =================== Конфигурация ===================
aruco_type = "DICT_4X4_100"
marker_size_m = 0.05  # ←←← УКАЖИ РЕАЛЬНЫЙ ФИЗИЧЕСКИЙ РАЗМЕР МАРКЕРА В МЕТРАХ!

intrinsic_camera = np.array([[933.15867,   0,       657.59],
                             [0,         933.1586, 400.36993],
                             [0,           0,          1]], dtype=np.float32)

distortion = np.array([-0.43948, 0.18514, 0, 0, 0], dtype=np.float32)  # добавил нулевой коэффициент, если нужно

# =================== Запуск камеры ===================
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    output = pose_estimation(frame, ARUCO_DICT[aruco_type],
                             intrinsic_camera, distortion, marker_size=marker_size_m)

    cv2.imshow('ArUco Pose Estimation', output)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()