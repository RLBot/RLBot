#pragma once

#include <vector>
#include <string>

#include "simulation/bvh.h"
#include "simulation/geometry.h"

class Field {

  struct wall {
    vec3 p;
    vec3 n;
    bool collidable;
  };

 public:
  static bvh<tri> collision_mesh;
  static bvh<sphere> navigation_mesh;
  static std::vector<wall> walls;
  static std::vector<tri> triangles;
  static std::vector<aabb> obstacles;
  static float r;
  static float R;
  static std::string mode;

  static bool initialize_soccar();
  static bool initialize_hoops();
  static bool initialize_dropshot();

  static ray snap(vec3 p);
  static ray collide(const obb & o);
  static ray collide(const aabb & a);
  static ray collide(const sphere & o);

  static ray raycast_any(const ray &);

  static void read_mesh_files(std::string);
  static void write_mesh_files();

};
