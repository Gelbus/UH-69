// I2CProtocol.h
#pragma once
#include <Arduino.h>
#include "Config.h"
#include "States.h"

// Типы команд от Raspberry Pi к Arduino
enum CommandType : uint8_t {
    CMD_HEARTBEAT = 0x01,
    CMD_MOVE = 0x02,
    CMD_STOP = 0x03,
    CMD_EMERGENCY_STOP = 0x04,
    CMD_GET_STATUS = 0x05
};

// Типы движения
enum MotionType : uint8_t {
    STRAIGHT = 0x01, //движение по прямой
    ROTATE = 0x02    // поворот на месте
};

// Статусы выполнения сегмента
enum SegmentStatus : uint8_t {
    SEG_IN_PROGRESS = 0x00,
    SEG_COMPLETED = 0x01,
    SEG_ABORTED = 0x02,
    SEG_BLOCKED = 0x03      // Сегмент прерван из-за препятствия
};

enum SafetyState : uint8_t {
    SAFETY_OK = 0x00,       // Путь свободен
    SAFETY_SLOWDOWN = 0x01, // Замедление из-за препятствия
    SAFETY_BLOCKED = 0x02,  // Путь заблокирован
    SAFETY_EMERGENCY = 0x03 // Аварийная ситуация
};

// Типы ошибок
enum ErrorType : uint8_t {
    ERROR_NONE = 0x00,
    ERROR_COMM = 0x01,      // Ошибка связи
    ERROR_MOTOR = 0x02,     // Ошибка мотора
    ERROR_SAFETY = 0x03,    // Ошибка безопасности
    ERROR_TIMEOUT = 0x04    // Таймаут выполнения
};

// Типы телеметрии от Arduino к Raspberry Pi
enum TelemetryType : uint8_t {
    TELEMETRY_SEGMENT_PROGRESS = 0x20, // Прогресс выполнения сегмента
    TELEMETRY_STATUS = 0x21,           // Общий статус системы(FSM)
    TELEMETRY_ERROR = 0x22,            // Ошибка
    TELEMETRY_SENSOR_DATA = 0x23        // Данные с датчиков
};

// Структуры команд
#pragma pack(push, 1)  // Выравнивание по 1 байту для компактности

// Базовая структура для всех команд
struct CommandHeader {
    uint8_t startByte;    // 0xAA - маркер начала
    CommandType commandType;
    uint8_t packetId;     // ID пакета для подтверждения
};

// Команда движения (объединённая для движения и поворотов)
struct MoveCommand {
    CommandHeader header;
    uint8_t segmentId;     // Уникальный ID сегмента (1-255) (для сопоставления с телеметрией)
    MotionType motionType;
    int16_t targetValue;   // Целевое значение: для движения - мм, для поворота - градусы*10
    uint8_t maxSpeed;      // Максимальная скорость: 0-255 = 0-2.55 м/с (движение) или 0-25.5 град/с (поворот)
    uint8_t maxAccel;      // Максимальное ускорение: 0-255 = 0-2.55 м/с² (движение) или 0-25.5 град/с² (поворот)
    uint8_t checksum;
};

// Heartbeat команда
struct HeartbeatCommand {
    CommandHeader header;
    uint32_t timestamp_ms; // Временная метка от Pi
    uint8_t checksum;
};

// Структуры телеметрии
struct TelemetryHeader {
    uint8_t startByte;    // 0xBB - маркер начала
    TelemetryType telemetryType;
    uint8_t packetId;
};

// Телеметрия прогресса выполнения сегмента
struct SegmentProgressTelemetry {
    TelemetryHeader header;
    uint8_t segmentId;         // ID текущего сегмента
    MotionType motionType;
    int16_t currentProgress;   // Текущий прогресс:   для движения: преодолённое расстояние в мм;   для поворота: текущий угол в градусах*10
    int16_t targetProgress;    // Целевой прогресс (копия из команды для удобства)
    uint8_t status;            // 0=IN_PROGRESS, 1=COMPLETED, 2=ABORTED
    uint8_t checksum;
};

// Телеметрия статуса
struct StatusTelemetry {
    TelemetryHeader header;
    RobotState fsmState;   
    SafetyState safetyState;   // Состояние безопасности
    uint16_t minObstacleDistance; // Минимальное расстояние до препятствия в см
    uint8_t checksum;
};

// Телеметрия ошибок
struct ErrorTelemetry {
    TelemetryHeader header;
    uint16_t error_code;
    ErrorType errorType;       // Тип ошибки
    uint8_t segmentId;         // ID сегмента, при котором произошла ошибка
    uint8_t checksum;
};

#pragma pack(pop)

// Вспомогательные функции для работы с протоколом
class I2CProtocol {
public:
    static uint8_t calculateChecksum(const void* data, size_t length) {
        const uint8_t* bytes = static_cast<const uint8_t*>(data);
        uint8_t checksum = 0;
        for (size_t i = 0; i < length - 1; i++) {
            checksum ^= bytes[i];
        }
        return checksum;
    }
    
    static bool validatePacket(const void* packet, size_t length) {
        if (length < 4) return false; // Минимальный размер пакета
        
        const uint8_t* bytes = static_cast<const uint8_t*>(packet);
        return bytes[0] == 0xAA && bytes[length - 1] == calculateChecksum(packet, length);
    }
    
    static int16_t degreesToFixedPoint(float degrees) {
        return static_cast<int16_t>(round(degrees * 10.0f)); // *10 для точности до 0.1°
    }
    
    static float fixedPointToDegrees(int16_t value) {
        return static_cast<float>(value) / 10.0f;
    }
    
    // Проверка валидности параметров движения
    static bool isValidMotionParams(uint8_t maxSpeed, uint8_t maxAccel) {
        // Проверка на разумные значения (не нулевые и не слишком большие)
        return (maxSpeed > 5 && maxSpeed <= 255) && (maxAccel > 5 && maxAccel <= 255);
    }
    
    // Преобразование скорости из м/с в код
    static uint8_t mpsToCode(float mps) {
        return constrain(static_cast<uint8_t>(round(mps * 100.0f)), 0, 255);
    }
    
    // Преобразование ускорения из м/с² в код
    static uint8_t mps2ToCode(float mps2) {
        return constrain(static_cast<uint8_t>(round(mps2 * 100.0f)), 0, 255);
    }
};

// Константы для протокола
namespace ProtocolConstants {
    static constexpr uint8_t MAX_SEGMENT_ID = 255;
    static constexpr uint32_t COMMAND_TIMEOUT_MS = 5000; // Таймаут команды
    static constexpr uint32_t HEARTBEAT_INTERVAL_MS = 200; // Интервал heartbeat
    static constexpr uint8_t MAX_RETRIES = 3; // Максимальное количество попыток
}