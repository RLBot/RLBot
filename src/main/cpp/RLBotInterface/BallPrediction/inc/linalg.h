#pragma once

#include <math.h>

#include "vec.h"
#include "mat.h"

template < int m, int n >
inline vec < n > dot(const vec < m > & v,
                     const mat < m, n > & A) {

  vec < n > vA;

  for(int i = 0; i < n; i++){
    vA(i) = 0;
    for(int j = 0; j < m; j++){
      vA(i) += v(j) * A(j,i);
    }
  }

  return vA;

}

template < int m, int n >
inline vec < m > dot(const mat < m, n > & A,
                     const vec < n > & v) {
                           

  vec < m > Av;

  for(int i = 0; i < m; i++){
    Av(i) = 0;
    for(int j = 0; j < n; j++){
      Av(i) += A(i,j) * v(j);
    }
  }

  return Av;

}

template < int m, int n >
inline float dot(const vec < m > & u,
                 const mat < m, n > & A,
                 const vec < n > & v) {
                           
  float uAv = 0;

  for(int i = 0; i < m; i++){
    for(int j = 0; j < n; j++){
      uAv += u(i) * A(i,j) * v(j);
    }
  }

  return uAv;

}

inline float sgn(float x) { 
  return float((0.0f < x) - (x < 0.0f)); 
}

inline float clamp(float x, float minimum, float maximum) {
  return fmax(fmin(x, maximum), minimum);
}
