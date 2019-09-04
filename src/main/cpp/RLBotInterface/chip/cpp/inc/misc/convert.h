#pragma once

#include "linear_algebra/math.h"

#ifdef GENERATE_PYTHON_BINDINGS
#include <pybind11/pybind11.h>
namespace convert {
  vec3 vector3_to_vec3(pybind11::object vector3);
  mat3 rotator_to_mat3(pybind11::object rotator);
}
#endif
