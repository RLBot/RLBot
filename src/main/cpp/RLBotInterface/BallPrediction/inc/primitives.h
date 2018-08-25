#pragma once

#include <math.h>
#include <iostream>

#include "linalg.h"

struct int2{
  int32_t x, y;
};

inline bool operator<(const int2 & a, const int2 & b) { 
  return (a.x < b.x) || (a.x == b.x && a.y < b.y);
}

struct interval{
  float minimum, maximum;
};

struct ray{
  vec3 start, direction;
};

struct sphere{
  vec3 center;
  float radius;
};

struct tri{

  vec3 p[3];

  tri(){}
  tri(std::initializer_list< vec3 >);

  inline vec3 center(){ 
    return (p[0] + p[1] + p[2]) / 3.0f;
  }

  inline vec3 unit_normal(){ 
    return normalize(cross(p[1]-p[0], p[2]-p[0])); 
  }

};

struct obb{

  vec3 center;
  vec3 half_width;
  mat3 orientation;

  obb(){}

};

struct aabb{

  float min_x;
  float min_y;
  float min_z;

  float max_x;
  float max_y;
  float max_z;

  aabb(){}
  aabb(const tri &);
  aabb(const obb &);
  aabb(const sphere & s);
  aabb(const aabb & a, const aabb & b);

  inline vec3 center() const{
    return vec3{0.5f * (min_x + max_x),
                0.5f * (min_y + max_y),
                0.5f * (min_z + max_z)};
  }

};

bool intersect(const aabb &, const aabb &);
bool intersect(const aabb &, const obb &);
bool intersect(const aabb &, const tri &);
bool intersect(const aabb &, const sphere &);

bool intersect(const obb &, const aabb &);
bool intersect(const obb &, const obb &);
bool intersect(const obb &, const tri &);
bool intersect(const obb &, const sphere &);

bool intersect(const tri &, const aabb &);
bool intersect(const tri &, const obb &);
bool intersect(const tri &, const tri &);
bool intersect(const tri &, const sphere &);

bool intersect(const sphere &, const aabb &);
bool intersect(const sphere &, const obb &);
bool intersect(const sphere &, const tri &);
bool intersect(const sphere &, const sphere &);

template < typename T >
interval project_along_axis(const T &, const vec3 &);
