#pragma once

#include <array>
#include <vector>
#include <string>
#include <fstream>

#include "simulation/car.h"
#include "simulation/ball.h"
#include "simulation/pad.h"
#include "simulation/goal.h"

#ifdef GENERATE_PYTHON_BINDINGS
#include <pybind11/pybind11.h>
#endif

class Game {
 public:
  Game(int, int);

  int id;
  int team;

  int frame;
  int frame_delta;

  float time;
  float time_delta;
  float time_remaining;

  int num_cars;
  bool overtime;
  bool round_active;
  bool kickoff_pause;
  bool match_ended;

  static float gravity;
  static float frametime;
  static std::string map;
  static std::string mode;

  Car * my_car;

  Ball ball;

  std::array< Car, 8 > cars;

  std::vector< Pad > pads;

//  void log(std::string);

  static void set_mode(std::string);

  #ifdef GENERATE_PYTHON_BINDINGS
  void read_game_information(pybind11::object gametick_packet,
                             pybind11::object phystick_packet,
                             pybind11::object fieldinfo_packet);
  #endif

 private:

//  std::ofstream logfile;
//  std::string log_filename;

  std::array < float, 16 > delta_history;

};
