#pragma once

#include <math.h>
#include <iostream>
#include <initializer_list>

template <int n>
class vec {
  float data[n];

 public:
  vec() {}

  explicit vec(float value) {
    for (int i = 0; i < n; i++) {
      data[i] = value;
    }
  }

  vec(std::initializer_list<float> args) {
    int i = 0;
    for (float arg : args) {
      data[i++] = arg;
    }
  }

  template <int m>
  vec(const vec<m>& other) {
    for (int i = 0; i < n; i++) {
      data[i] = (i < m) ? other[i] : 0.0f;
    }
  }

  constexpr float& operator[](const size_t i) { return data[i]; }
  constexpr float operator[](const size_t i) const { return data[i]; }
  constexpr float& operator()(const size_t i) { return data[i]; }
  constexpr float operator()(const size_t i) const { return data[i]; }

  // elementwise addition
  vec<n> operator+(const vec<n>& other) const {
    vec<n> v;
    for (int i = 0; i < n; i++) {
      v[i] = data[i] + other[i];
    }
    return v;
  }

  // elementwise multiplication
  vec<n> operator*(const vec<n>& other) const {
    vec<n> v;
    for (int i = 0; i < n; i++) {
      v[i] = data[i] * other[i];
    }
    return v;
  }

  // in-place elementwise addition
  vec<n>& operator+=(const vec<n>& other) {
    for (int i = 0; i < n; i++) {
      data[i] += other[i];
    }
    return *this;
  }

  // unary minus
  vec<n> operator-() const {
    vec<n> v;
    for (int i = 0; i < n; i++) {
      v[i] = -data[i];
    }
    return v;
  }

  // elementwise subtraction
  vec<n> operator-(const vec<n>& other) const {
    vec<n> v;
    for (int i = 0; i < n; i++) {
      v[i] = data[i] - other[i];
    }
    return v;
  }

  // in-place elementwise subtraction
  vec<n>& operator-=(const vec<n>& other) {
    for (int i = 0; i < n; i++) {
      data[i] -= other[i];
    }
    return *this;
  }

  // in-place scalar addition
  vec<n>& operator+=(const float other) {
    for (int i = 0; i < n; i++) {
      data[i] += other;
    }
    return *this;
  }

  // in-place scalar multiplication
  vec<n>& operator*=(const float other) {
    for (int i = 0; i < n; i++) {
      data[i] *= other;
    }
    return *this;
  }

  // in-place scalar division
  vec<n>& operator/=(const float other) {
    for (int i = 0; i < n; i++) {
      data[i] /= other;
    }
    return *this;
  }
};

inline vec<3> cross(const vec<3>& a, const vec<3>& b) {
  return { a(1) * b(2) - a(2) * b(1), a(2) * b(0) - a(0) * b(2),
      a(0) * b(1) - a(1) * b(0) };
}

inline vec<3> cross(const vec<3>& a) { return { -a(1), a(0), 0.0f }; }

inline vec<2> cross(const vec<2>& a) { return { -a(1), a(0) }; }

inline float det(const vec<2>& a, const vec<2>& b) { return a(0) * b(1) - a(1) * b(0); }

template <int n>
inline float norm(const vec<n>& v) {
  return sqrt(dot(v, v));
}

template <int n>
inline vec<n> normalize(const vec<n>& v) {
  float norm_v = norm(v);
  if (norm_v < 1.0e-6) {
    return vec<n>(0.0f);
  }
  else {
    return v / norm_v;
  }
}

template <int n>
inline vec<n> operator*(const vec<n>& v, const float other) {
  vec<n> u;
  for (int i = 0; i < n; i++) {
    u(i) = other * v(i);
  }
  return u;
}

template <int n>
inline vec<n> operator*(const float other, const vec<n>& v) {
  vec<n> u;
  for (int i = 0; i < n; i++) {
    u(i) = other * v(i);
  }
  return u;
}

template <int n>
inline vec<n> operator/(const vec<n>& v, const float other) {
  vec<n> u;
  for (int i = 0; i < n; i++) {
    u(i) = v(i) / other;
  }
  return u;
}

template <int n>
inline vec<n> operator/(const float other, const vec<n>& v) {
  vec<n> u;
  for (int i = 0; i < n; i++) {
    u(i) = other / v(i);
  }
  return u;
}

inline float atan2(const vec<2>& v) { return atan2(v(1), v(0)); }

template <int n>
inline float dot(const vec<n>& u, const vec<n>& v) {
  float a = 0.0;
  for (int i = 0; i < n; i++) {
    a += u[i] * v[i];
  }
  return a;
}

template <int d>
std::ostream& operator<<(std::ostream& os, const vec<d>& v) {
  for (int i = 0; i < d; i++) {
    os << v[i];
    if (i != d-1) os << ", ";
  }
  return os;
}

typedef vec<2> vec2;
typedef vec<3> vec3;
typedef vec<4> vec4;
