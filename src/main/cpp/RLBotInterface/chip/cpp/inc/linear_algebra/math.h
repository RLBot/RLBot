#pragma once

#include <math.h>
#include <algorithm>

#include "vec.h"
#include "mat.h"

template < int m, int n >
inline vec < n > dot(const vec < m > & v,
  const mat < m, n > & A) {

  vec < n > vA;

  for (int i = 0; i < n; i++) {
    vA(i) = 0;
    for (int j = 0; j < m; j++) {
      vA(i) += v(j) * A(j, i);
    }
  }

  return vA;

}

template < int m, int n >
inline vec < m > dot(const mat < m, n > & A,
  const vec < n > & v) {

  vec < m > Av;

  for (int i = 0; i < m; i++) {
    Av(i) = 0;
    for (int j = 0; j < n; j++) {
      Av(i) += A(i, j) * v(j);
    }
  }

  return Av;

}

template < int m, int n >
inline float dot(const vec < m > & u,
  const mat < m, n > & A,
  const vec < n > & v) {

  float uAv = 0;

  for (int i = 0; i < m; i++) {
    for (int j = 0; j < n; j++) {
      uAv += u(i) * A(i, j) * v(j);
    }
  }

  return uAv;

}

inline float sgn(float x) {
  return float((0.0f < x) - (x < 0.0f));
}

inline float clip(float x, float minimum, float maximum) {
  return fmax(fmin(x, maximum), minimum);
}

template < typename T >
inline T clip(const T x, const T minimum, const T maximum) {
  return std::max(std::min(x, maximum), minimum);
}

inline float angle_between(const vec < 2 > & a, const vec < 2 > & b) {
  return acos(clip(dot(normalize(a), normalize(b)), -1.0f, 1.0f));
}

inline float angle_between(const vec < 3 > & a, const vec < 3 > & b) {
  return acos(clip(dot(normalize(a), normalize(b)), -1.0f, 1.0f));
}

// angle between proper orthogonal matrices
inline float angle_between(const mat < 3, 3 > & U, const mat < 3, 3 > & V) {
  return acos(0.5f * (tr(dot(U, transpose(V))) - 1.0f));
}

inline vec < 3 > xy(const vec < 3 > & v) {
  return vec < 3 >{v[0], v[1], 0.0f};
}

inline mat < 2, 2 > rotation(const float theta) {
  return mat< 2, 2 >{
    {cos(theta), -sin(theta)},
    { sin(theta), cos(theta) }
  };
}

inline mat < 3, 3 > axis_to_rotation(const vec < 3 > & omega) {

  float norm_omega = norm(omega);

  if (fabs(norm_omega) < 0.000001f) {

    return eye< 3 >();

  } else {

#if 0
    vec3 axis = normalize(omega);

    mat < 3, 3 > K = {
      {  0.0f  , -axis[2],  axis[1]},
      { axis[2],    0.0f , -axis[0]},
      {-axis[1],  axis[0],    0.0f }
    };

    return eye< 3 >() + sin(norm_omega) * K + (1.0f - cos(norm_omega)) * dot(K, K);
#else
    vec3 u = omega / norm_omega;

    float c = cos(norm_omega);
    float s = sin(norm_omega);

    return mat < 3, 3 >{
      {
        u[0]*u[0]*(1.0f - c) + c,
        u[0]*u[1]*(1.0f - c) - u[2]*s,
        u[0]*u[2]*(1.0f - c) + u[1]*s
      },{
        u[1]*u[0]*(1.0f - c) + u[2]*s,
        u[1]*u[1]*(1.0f - c) + c,
        u[1]*u[2]*(1.0f - c) - u[0]*s
      },{
        u[2]*u[0]*(1.0f - c) - u[1]*s,
        u[2]*u[1]*(1.0f - c) + u[0]*s,
        u[2]*u[2]*(1.0f - c) + c
      }
    };

#endif

  }

}

inline vec < 3 > rotation_to_axis(const mat < 3, 3 > & R) {

  float theta = acos(clip(0.5f * (tr(R) - 1.0f), -1.0f, 1.0f));

  float scale;

  // for small angles, prefer series expansion to division by sin(theta) ~ 0
  if (fabs(theta) < 0.00001f) {
    scale = 0.5f + theta * theta / 12.0f;
  }
  else {
    scale = 0.5f * theta / sin(theta);
  }

  return vec3{ R(2,1) - R(1,2), R(0,2) - R(2,0), R(1,0) - R(0,1) } *scale;

}

inline mat<3, 3> antisym(const vec<3>& w) {
  // clang-format off
  return mat < 3, 3 >{
    {  0.0, -w[2], w[1]},
    { w[2],   0.0, -w[0] },
    { -w[1],  w[0],   0.0 }
  };
  // clang-format on
}

inline mat<3, 3> euler_to_rotation(const vec<3>& pyr) {
  float CP = cos(pyr[0]);
  float SP = sin(pyr[0]);
  float CY = cos(pyr[1]);
  float SY = sin(pyr[1]);
  float CR = cos(pyr[2]);
  float SR = sin(pyr[2]);

  mat<3, 3> theta;

  // front direction
  theta(0, 0) = CP * CY;
  theta(1, 0) = CP * SY;
  theta(2, 0) = SP;

  // left direction
  theta(0, 1) = CY * SP * SR - CR * SY;
  theta(1, 1) = SY * SP * SR + CR * CY;
  theta(2, 1) = -CP * SR;

  // up direction
  theta(0, 2) = -CR * CY * SP - SR * SY;
  theta(1, 2) = -CR * SY * SP + SR * CY;
  theta(2, 2) = CP * CR;

  return theta;
}

// to use this with the quaternions directly from Rocket League,
// you have to do the following:
//
// vec4 q = get_quaternion_from_phys_tick();
// mat3 theta = quaterion_rotation(-q[3], -q[0], -q[1], -q[2])
//
inline mat<3, 3> quaternion_to_rotation(vec4 q) {

  float s = 1.0f / dot(q, q);

  mat<3, 3> theta;

  // front direction
  theta(0, 0) = 1.0f - 2.0f * s * (q[2] * q[2] + q[3] * q[3]);
  theta(1, 0) = 2.0f * s * (q[1] * q[2] + q[3] * q[0]);
  theta(2, 0) = 2.0f * s * (q[1] * q[3] - q[2] * q[0]);

  // left direction
  theta(0, 1) = 2.0f * s * (q[1] * q[2] - q[3] * q[0]);
  theta(1, 1) = 1.0f - 2.0f * s * (q[1] * q[1] + q[3] * q[3]);
  theta(2, 1) = 2.0f * s * (q[2] * q[3] + q[1] * q[0]);

  // up direction
  theta(0, 2) = 2.0f * s * (q[1] * q[3] + q[2] * q[0]);
  theta(1, 2) = 2.0f * s * (q[2] * q[3] - q[1] * q[0]);
  theta(2, 2) = 1.0f - 2.0f * s * (q[1] * q[1] + q[2] * q[2]);

  return theta;
}

inline mat < 3, 3 > look_at(const vec < 3 > & direction, const vec < 3 > & up = vec3{ 0.0f, 0.0f, 1.0f }) {
  vec3 f = normalize(direction);
  vec3 u = normalize(cross(f, cross(up, f)));
  vec3 l = normalize(cross(u, f));

  return mat3{
    {f[0], l[0], u[0]},
    {f[1], l[1], u[1]},
    {f[2], l[2], u[2]}
  };
}

inline mat < 3, 3 > R3_basis(const vec3 & n) {
  float sign = (n[2] >= 0.0f) ? 1.0f : -1.0f;
  float a = -1.0f / (sign + n[2]); 
  float b = n[0] * n[1] * a;

  return mat < 3, 3 >{
    {
      1.0f + sign * n[0] * n[0] * a,
      b,
      n[0],
    },{
      sign * b,
      sign + n[1] * n[1] * a,
      n[1]
    },{
      -sign * n[0],
      -n[1],
      n[2]
    }
  };
}

template < typename T >
inline T lerp(const T & a, const T & b, float t) {
  return a * (1.0f - t) + b * t;
}

#include <vector>
inline float standard_deviation(const std::vector < float > values) {

  size_t n = values.size();

  float E_x = 0.0f;
  float E_xsq = 0.0f;

  for (size_t i = 0; i < n; i++) {
    E_x += values[i];
    E_xsq += values[i] * values[i];
  }

  E_x /= n;
  E_xsq /= n;

  float bessel_correction = sqrt(float(n) / float(n-1));

  return bessel_correction * sqrt(E_xsq - E_x * E_x);

}

inline float mean(const std::vector < float > values) {

  float E_x = 0.0f;

  for (size_t i = 0; i < values.size(); i++) {
    E_x += values[i];
  }

  return E_x;

}
