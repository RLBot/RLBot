#pragma once

#include "linalg.h"

struct DynamicState {
  vec3 x;
  vec3 v;
  vec3 w;
  mat3 o;
};
