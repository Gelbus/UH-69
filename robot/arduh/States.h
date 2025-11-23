// States.h
#pragma once
#include <Arduino.h>

enum RobotState: uint8_t {
  STATE_IDLE,
  STATE_MOVING,
  STATE_TURNING,
  STATE_BRAKING,
  STATE_BLOCKED,
  STATE_ERROR,
  STATE_ESTOP
};