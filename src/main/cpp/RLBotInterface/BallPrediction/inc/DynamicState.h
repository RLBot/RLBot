#pragma once

#include "linalg.h"

struct DynamicState {
  vec3 x; // Location
  vec3 v; // Velocity
  vec3 w; // Angular velocity
  mat3 o; // Orientation
};
