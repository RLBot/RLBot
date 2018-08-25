#include "..\inc\primitives.h"

bool intersect(const interval & a, const interval & b) {
  return (a.minimum <= b.maximum) && (a.maximum >= b.minimum);
}

bool intersect(const aabb & a, const aabb & b) {
  return ((a.min_x <= b.max_x) & (a.max_x >= b.min_x) & 
          (a.min_y <= b.max_y) & (a.max_y >= b.min_y) & 
          (a.min_z <= b.max_z) & (a.max_z >= b.min_z));
}

template <>
interval project_along_axis(const aabb & a, const vec3 & axis) {

  vec3 abs_axis{fabs(axis[0]), fabs(axis[1]), fabs(axis(2))};
  vec3 center = 0.5f * vec3{a.max_x+a.min_x, a.max_y+a.min_y, a.max_z+a.min_z};
  vec3 diagonal{a.max_x - a.min_x, a.max_y - a.min_y, a.max_z - a.min_z};

  float i_center = dot(axis, center);
  float i_radius = 0.5f * dot(abs_axis, diagonal);

  return interval{i_center - i_radius, i_center + i_radius};

}

template <>
interval project_along_axis(const obb & a, const vec3 & axis) {

  vec3 raxis = dot(axis, a.orientation); 
  vec3 abs_raxis{fabs(raxis[0]), fabs(raxis[1]), fabs(raxis(2))};

  float i_center = dot(axis, a.center); 
  float i_radius = dot(abs_raxis, a.half_width);

  return interval{i_center - i_radius, i_center + i_radius};

}

template <>
interval project_along_axis(const tri & a, const vec3 & axis) {

  float value;
  interval i;

  value = dot(a.p[0], axis);
  i.minimum = i.maximum = value;

  value = dot(a.p[1], axis);
  i.minimum = fminf(value, i.minimum);
  i.maximum = fmaxf(value, i.maximum);

  value = dot(a.p[2], axis);
  i.minimum = fminf(value, i.minimum);
  i.maximum = fmaxf(value, i.maximum);

  return i;

}

template < typename S, typename T >
bool separated_along_axis(const S & a, const T & b, const vec3 & axis) {
  auto a_interval = project_along_axis(a, axis);
  auto b_interval = project_along_axis(b, axis);
  return (intersect(a_interval, b_interval) == false);
}

bool intersect(const aabb & a, const obb & b) {
  
  vec3 e1{1.0f, 0.0f, 0.0f};
  vec3 e2{0.0f, 1.0f, 0.0f};
  vec3 e3{0.0f, 0.0f, 1.0f};

  vec3 o1{b.orientation(0, 0), b.orientation(1, 0), b.orientation(2, 0)};
  vec3 o2{b.orientation(0, 1), b.orientation(1, 1), b.orientation(2, 1)};
  vec3 o3{b.orientation(0, 2), b.orientation(1, 2), b.orientation(2, 2)};

  if (separated_along_axis(a, b, e1)) return false;
  if (separated_along_axis(a, b, e2)) return false;
  if (separated_along_axis(a, b, e3)) return false;

  if (separated_along_axis(a, b, o1)) return false;
  if (separated_along_axis(a, b, o2)) return false;
  if (separated_along_axis(a, b, o3)) return false;

  if (separated_along_axis(a, b, cross(e1, o1))) return false;
  if (separated_along_axis(a, b, cross(e1, o2))) return false;
  if (separated_along_axis(a, b, cross(e1, o3))) return false;

  if (separated_along_axis(a, b, cross(e2, o1))) return false;
  if (separated_along_axis(a, b, cross(e2, o2))) return false;
  if (separated_along_axis(a, b, cross(e2, o3))) return false;

  if (separated_along_axis(a, b, cross(e3, o1))) return false;
  if (separated_along_axis(a, b, cross(e3, o2))) return false;
  if (separated_along_axis(a, b, cross(e3, o3))) return false;

  return true;

}

bool intersect(const obb & a, const aabb & b) {
  return intersect(b, a);
}

bool intersect(const aabb & a, const tri & b) {

  vec3 e1{1.0f, 0.0f, 0.0f};
  vec3 e2{0.0f, 1.0f, 0.0f};
  vec3 e3{0.0f, 0.0f, 1.0f};

  vec3 t1 = b.p[1] - b.p[0];
  vec3 t2 = b.p[2] - b.p[1];
  vec3 t3 = b.p[0] - b.p[2];

  if (separated_along_axis(a, b, cross(t1, t2))) return false;

  if (separated_along_axis(a, b, e1)) return false;
  if (separated_along_axis(a, b, e2)) return false;
  if (separated_along_axis(a, b, e3)) return false;

  if (separated_along_axis(a, b, cross(e1, t1))) return false;
  if (separated_along_axis(a, b, cross(e1, t2))) return false;
  if (separated_along_axis(a, b, cross(e1, t3))) return false;

  if (separated_along_axis(a, b, cross(e2, t1))) return false;
  if (separated_along_axis(a, b, cross(e2, t2))) return false;
  if (separated_along_axis(a, b, cross(e2, t3))) return false;

  if (separated_along_axis(a, b, cross(e3, t1))) return false;
  if (separated_along_axis(a, b, cross(e3, t2))) return false;
  if (separated_along_axis(a, b, cross(e3, t3))) return false;
      
  return true;

}

bool intersect(const tri & a, const aabb & b) {
  return intersect(b, a);
}

bool intersect(const aabb & a, const sphere & b) {

  vec3 nearest {
    clamp(b.center[0], a.min_x, a.max_x),
    clamp(b.center[1], a.min_y, a.max_y),
    clamp(b.center[2], a.min_z, a.max_z)
  };

  return (norm(b.center - nearest) <= b.radius);

}

bool intersect(const sphere & a, const aabb & b) {
  return intersect(b, a);
}

bool intersect(const obb & a, const obb & b) {
  
  vec3 e1{a.orientation(0, 0), a.orientation(1, 0), a.orientation(2, 0)};
  vec3 e2{a.orientation(0, 1), a.orientation(1, 1), a.orientation(2, 1)};
  vec3 e3{a.orientation(0, 2), a.orientation(1, 2), a.orientation(2, 2)};

  vec3 o1{b.orientation(0, 0), b.orientation(1, 0), b.orientation(2, 0)};
  vec3 o2{b.orientation(0, 1), b.orientation(1, 1), b.orientation(2, 1)};
  vec3 o3{b.orientation(0, 2), b.orientation(1, 2), b.orientation(2, 2)};

  if (separated_along_axis(a, b, e1)) return false;
  if (separated_along_axis(a, b, e2)) return false;
  if (separated_along_axis(a, b, e3)) return false;

  if (separated_along_axis(a, b, o1)) return false;
  if (separated_along_axis(a, b, o2)) return false;
  if (separated_along_axis(a, b, o3)) return false;

  if (separated_along_axis(a, b, cross(e1, o1))) return false;
  if (separated_along_axis(a, b, cross(e1, o2))) return false;
  if (separated_along_axis(a, b, cross(e1, o3))) return false;

  if (separated_along_axis(a, b, cross(e2, o1))) return false;
  if (separated_along_axis(a, b, cross(e2, o2))) return false;
  if (separated_along_axis(a, b, cross(e2, o3))) return false;

  if (separated_along_axis(a, b, cross(e3, o1))) return false;
  if (separated_along_axis(a, b, cross(e3, o2))) return false;
  if (separated_along_axis(a, b, cross(e3, o3))) return false;

  return true;

}

bool intersect(const obb & a, const tri & b) {

  vec3 e1{a.orientation(0, 0), a.orientation(1, 0), a.orientation(2, 0)};
  vec3 e2{a.orientation(0, 1), a.orientation(1, 1), a.orientation(2, 1)};
  vec3 e3{a.orientation(0, 2), a.orientation(1, 2), a.orientation(2, 2)};

  vec3 t1 = b.p[1] - b.p[0];
  vec3 t2 = b.p[2] - b.p[1];
  vec3 t3 = b.p[0] - b.p[2];

  if (separated_along_axis(a, b, cross(t1, t2))) return false;

  if (separated_along_axis(a, b, e1)) return false;
  if (separated_along_axis(a, b, e2)) return false;
  if (separated_along_axis(a, b, e3)) return false;

  if (separated_along_axis(a, b, cross(e1, t1))) return false;
  if (separated_along_axis(a, b, cross(e1, t2))) return false;
  if (separated_along_axis(a, b, cross(e1, t3))) return false;

  if (separated_along_axis(a, b, cross(e2, t1))) return false;
  if (separated_along_axis(a, b, cross(e2, t2))) return false;
  if (separated_along_axis(a, b, cross(e2, t3))) return false;

  if (separated_along_axis(a, b, cross(e3, t1))) return false;
  if (separated_along_axis(a, b, cross(e3, t2))) return false;
  if (separated_along_axis(a, b, cross(e3, t3))) return false;
      
  return true;

}

bool intersect(const tri & a, const obb & b) {
  return intersect(b, a);
}

bool intersect(const obb & a, const sphere & b) {

  vec3 p = dot(b.center - a.center, a.orientation); 
  vec3 q {
    p[0] * fmin(1.0f, a.half_width[0] / fabs(p[0])),
    p[1] * fmin(1.0f, a.half_width[1] / fabs(p[1])),
    p[2] * fmin(1.0f, a.half_width[2] / fabs(p[2]))
  };

  return (norm(p - q) <= b.radius);

}

bool intersect(const sphere & a, const obb & b) {
  return intersect(b, a);
}

bool intersect(const tri & a, const tri & b) {

  vec3 s1 = a.p[1] - a.p[0];
  vec3 s2 = a.p[2] - a.p[1];
  vec3 s3 = a.p[0] - a.p[2];

  vec3 t1 = b.p[1] - b.p[0];
  vec3 t2 = b.p[2] - b.p[1];
  vec3 t3 = b.p[0] - b.p[2];

  if (separated_along_axis(a, b, cross(s1, s2))) return false;
  if (separated_along_axis(a, b, cross(t1, t2))) return false;

  if (separated_along_axis(a, b, cross(s1, t1))) return false;
  if (separated_along_axis(a, b, cross(s1, t2))) return false;
  if (separated_along_axis(a, b, cross(s1, t3))) return false;

  if (separated_along_axis(a, b, cross(s2, t1))) return false;
  if (separated_along_axis(a, b, cross(s2, t2))) return false;
  if (separated_along_axis(a, b, cross(s2, t3))) return false;

  if (separated_along_axis(a, b, cross(s3, t1))) return false;
  if (separated_along_axis(a, b, cross(s3, t2))) return false;
  if (separated_along_axis(a, b, cross(s3, t3))) return false;
      
  return true;

}

float distance_between(const vec3 & start, const vec3 & dir, const vec3 & p) {

  float u = clamp(dot(p - start, dir) / dot(dir, dir), 0.0f, 1.0f);
  return norm(start + u * dir - p);

}

bool intersect(const tri & a, const sphere & b) {

  float dist;
    
  vec3 e1 = a.p[1] - a.p[0];
  vec3 e2 = a.p[2] - a.p[1];
  vec3 e3 = a.p[0] - a.p[2];
  vec3 n  = normalize(cross(e3, e1));

  mat3 A = {
    {e1[0], -e3[0], n[0]},
    {e1[1], -e3[1], n[1]},
    {e1[2], -e3[2], n[2]}
  };

  vec3 x = dot(inv(A), b.center - a.p[0]);

  float u = x[0];
  float v = x[1];
  float w = 1.0f - u - v;
  float z = x[2];

  // if the projection of sphere's center 
  // along the triangle normal puts it inside
  // the triangle, then we can just check
  // the out-of-plane distance
  if (0.0f <= u && u <= 1.0f &&
      0.0f <= v && v <= 1.0f &&
      0.0f <= w && w <= 1.0f) {

    dist = fabs(z);

  // otherwise, check the distances to
  // the closest edge of the triangle
  } else {

    dist = b.radius + 1.0f;
    dist = fmin(dist, distance_between(a.p[0], e1, b.center));
    dist = fmin(dist, distance_between(a.p[1], e2, b.center));
    dist = fmin(dist, distance_between(a.p[2], e3, b.center));
    
  }

  return dist <= b.radius;

}

bool intersect(const sphere & a, const tri & b) {
  return intersect(b, a);
}

bool intersect(const sphere & a, const sphere & b) {
  return norm(a.center - b.center) <= (a.radius + b.radius);
}

aabb::aabb(const tri & t) {

  min_x = fminf(t.p[0][0], fminf(t.p[1][0], t.p[2][0]));
  min_y = fminf(t.p[0][1], fminf(t.p[1][1], t.p[2][1]));
  min_z = fminf(t.p[0][2], fminf(t.p[1][2], t.p[2][2]));
  
  max_x = fmaxf(t.p[0][0], fmaxf(t.p[1][0], t.p[2][0]));
  max_y = fmaxf(t.p[0][1], fmaxf(t.p[1][1], t.p[2][1]));
  max_z = fmaxf(t.p[0][2], fmaxf(t.p[1][2], t.p[2][2]));

}

aabb::aabb(const obb & o) {

  interval x_range = project_along_axis(o, vec3{1.0f, 0.0f, 0.0f});
  min_x = x_range.minimum;
  max_x = x_range.maximum;

  interval y_range = project_along_axis(o, vec3{0.0f, 1.0f, 0.0f});
  min_y = y_range.minimum;
  max_y = y_range.maximum;

  interval z_range = project_along_axis(o, vec3{0.0f, 0.0f, 1.0f});
  min_z = z_range.minimum;
  max_z = z_range.maximum;

}

aabb::aabb(const sphere & s) {

  min_x = s.center[0] - s.radius;
  min_y = s.center[1] - s.radius;
  min_z = s.center[2] - s.radius;

  max_x = s.center[0] + s.radius;
  max_y = s.center[1] + s.radius;
  max_z = s.center[2] + s.radius;

}

aabb::aabb(const aabb & a, const aabb & b) {
  min_x = fminf(a.min_x, b.min_x);
  min_y = fminf(a.min_y, b.min_y);
  min_z = fminf(a.min_z, b.min_z);
  max_x = fmaxf(a.max_x, b.max_x);
  max_y = fmaxf(a.max_y, b.max_y);
  max_z = fmaxf(a.max_z, b.max_z);
}

tri::tri(std::initializer_list< vec3 > args) {
  int i = 0;
  for (auto arg : args) {
    p[i++] = arg;
  }
}
